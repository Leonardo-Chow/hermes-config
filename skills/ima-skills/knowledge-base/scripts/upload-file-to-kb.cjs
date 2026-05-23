#!/usr/bin/env node
/**
 * upload-file-to-kb.cjs
 *
 * One-step file upload to IMA knowledge base.
 * Avoids the COS token truncation bug (875+ char token gets cut in shell args).
 *
 * Usage:
 *   node scripts/upload-file-to-kb.cjs <file_path> <knowledge_base_id> [title]
 *
 * Example:
 *   node scripts/upload-file-to-kb.cjs /tmp/report.pdf "kb_id_here" "report.pdf"
 *
 * Dependencies: none (uses Node.js built-in https + crypto)
 */
'use strict';
const fs = require('fs');
const https = require('https');
const crypto = require('crypto');
const { spawn } = require('child_process');

const SKILL_DIR = __dirname.replace(/\/scripts$/, '').replace(/\/knowledge-base$/, '');

function callIMA(endpoint, body) {
  return new Promise((resolve, reject) => {
    const proc = spawn('node', [SKILL_DIR + '/ima_api.cjs', endpoint, JSON.stringify(body)], {
      stdio: ['inherit', 'pipe', 'pipe'],
    });
    let out = '', err = '';
    proc.stdout.on('data', (d) => out += d);
    proc.stderr.on('data', (d) => err += d);
    proc.on('close', (code) => {
      if (code !== 0) reject(new Error(err || `exit ${code}`));
      else try { resolve(JSON.parse(out)); } catch(e) { reject(new Error('JSON parse: ' + out)); }
    });
  });
}

async function main() {
  const filePath = process.argv[2];
  const kbId = process.argv[3];
  const title = process.argv[4] || require('path').basename(filePath);

  if (!filePath || !kbId) {
    console.error('Usage: node upload-file-to-kb.cjs <file_path> <knowledge_base_id> [title]');
    process.exit(1);
  }

  const stats = fs.statSync(filePath);
  const ext = filePath.split('.').pop().toLowerCase();
  const extToMime = {
    pdf: 'application/pdf', doc: 'application/msword',
    docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ppt: 'application/vnd.ms-powerpoint',
    pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    xls: 'application/vnd.ms-excel',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg',
    gif: 'image/gif', webp: 'image/webp', mp3: 'audio/mpeg',
    mp4: 'video/mp4', txt: 'text/plain', md: 'text/markdown',
  };
  const contentType = extToMime[ext] || 'application/octet-stream';
  const mediaTypeMap = {
    pdf: 1, doc: 3, docx: 3, ppt: 4, pptx: 4, xls: 5, xlsx: 5,
    png: 7, jpg: 7, jpeg: 7, gif: 9, mp3: 14, mp4: 13, txt: 1, md: 1,
  };
  const mediaType = mediaTypeMap[ext] || 1;

  // Step 1: create_media
  console.error('Creating media...');
  const mediaResp = await callIMA('openapi/wiki/v1/create_media', {
    file_name: require('path').basename(filePath),
    file_size: stats.size,
    content_type: contentType,
    knowledge_base_id: kbId,
    file_ext: ext,
  });
  if (mediaResp.code !== 0) throw new Error('create_media: ' + mediaResp.msg);
  const d = mediaResp.data;
  const c = d.cos_credential;
  console.error('Got COS credentials, uploading...');

  // Step 2: COS upload via raw HTTPS (avoids shell arg truncation of token)
  const fileContent = fs.readFileSync(filePath);
  const hostname = `${c.bucket_name}.cos.${c.region}.myqcloud.com`;
  const pathname = `/${c.cos_key}`;
  const keyTime = `${c.start_time};${c.expired_time}`;
  const signKey = crypto.createHmac('sha1', c.secret_key).update(keyTime).digest('hex');
  const httpString = `put\n${pathname}\n\ncontent-length=${encodeURIComponent(String(fileContent.length))}&host=${encodeURIComponent(hostname)}\n`;
  const stringToSign = `sha1\n${keyTime}\n${crypto.createHash('sha1').update(httpString).digest('hex')}\n`;
  const signature = crypto.createHmac('sha1', signKey).update(stringToSign).digest('hex');
  const authorization = [
    'q-sign-algorithm=sha1', `q-ak=${c.secret_id}`, `q-sign-time=${keyTime}`,
    `q-key-time=${keyTime}`, 'q-header-list=content-length;host', 'q-url-param-list=',
    `q-signature=${signature}`,
  ].join('&');

  await new Promise((resolve, reject) => {
    const cosReq = https.request({
      hostname, port: 443, path: pathname, method: 'PUT',
      headers: {
        'Content-Type': contentType, 'Content-Length': fileContent.length,
        'Authorization': authorization, 'x-cos-security-token': c.token,
      }, timeout: 300000,
    }, (cosRes) => {
      let body = '';
      cosRes.on('data', (chunk) => body += chunk);
      cosRes.on('end', () => {
        if (cosRes.statusCode >= 200 && cosRes.statusCode < 300) resolve();
        else reject(new Error(`COS ${cosRes.statusCode}: ${body}`));
      });
    });
    cosReq.on('error', reject);
    cosReq.write(fileContent);
    cosReq.end();
  });
  console.error('COS upload OK');

  // Step 3: add_knowledge
  console.error('Adding to knowledge base...');
  const addResp = await callIMA('openapi/wiki/v1/add_knowledge', {
    media_type: mediaType,
    media_id: d.media_id,
    title: title,
    knowledge_base_id: kbId,
    file_info: { cos_key: c.cos_key, file_size: stats.size, file_name: require('path').basename(filePath) },
  });
  if (addResp.code !== 0) throw new Error('add_knowledge: ' + addResp.msg);
  console.log(JSON.stringify({ success: true, media_id: d.media_id, title }));
}

main().catch((e) => { console.error('FATAL:', e.message); process.exit(1); });
