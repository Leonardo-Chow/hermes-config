#!/usr/bin/env node
/**
 * upload-to-kb.cjs — Unified IMA knowledge base file upload
 *
 * Usage: node upload-to-kb.cjs <file_path> <knowledge_base_id> [title]
 *
 * Runs create_media → COS upload → add_knowledge in a single Node.js process,
 * avoiding shell argument truncation of the 875+ char COS security token.
 *
 * Dependencies: None (uses Node.js built-in: https, crypto, fs, child_process)
 * The ima_api.cjs must be at: <SKILL_DIR>/ima_api.cjs (sibling to knowledge-base/)
 */

'use strict';
const fs = require('fs');
const path = require('path');
const https = require('https');
const crypto = require('crypto');
const { spawn } = require('child_process');

// ── Config ──
// Resolve ima_api.cjs relative to this script's location
const SCRIPT_DIR = path.dirname(fs.realpathSync(__filename));
const SKILL_DIR = path.resolve(SCRIPT_DIR, '..');      // knowledge-base/
const IMA_API = path.resolve(SKILL_DIR, '..', 'ima_api.cjs');  // ima-skills/ima_api.cjs

// ── Arg parsing ──
const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: node upload-to-kb.cjs <file_path> <knowledge_base_id> [title]');
  process.exit(1);
}
const FILE_PATH = args[0];
const KB_ID = args[1];
const FILE_TITLE = args[2] || path.basename(FILE_PATH);

if (!fs.existsSync(FILE_PATH)) {
  console.error(`File not found: ${FILE_PATH}`);
  process.exit(1);
}

// ── Helpers ──
function callIMA(endpoint, body) {
  return new Promise((resolve, reject) => {
    const proc = spawn('node', [IMA_API, endpoint, JSON.stringify(body)], {
      stdio: ['inherit', 'pipe', 'pipe'],
    });
    let out = '', err = '';
    proc.stdout.on('data', (d) => (out += d));
    proc.stderr.on('data', (d) => (err += d));
    proc.on('close', (code) => {
      if (code !== 0) return reject(new Error(err || `exit ${code}`));
      try { resolve(JSON.parse(out)); } catch (e) { reject(new Error(`JSON parse error: ${out}`)); }
    });
  });
}

function hmacSha1(key, data) {
  return crypto.createHmac('sha1', key).update(data).digest('hex');
}

function sha1(data) {
  return crypto.createHash('sha1').update(data).digest('hex');
}

async function main() {
  const stats = fs.statSync(FILE_PATH);
  const ext = path.extname(FILE_PATH).replace(/^\./, '').toLowerCase();
  const fileName = path.basename(FILE_PATH);
  const fileSize = stats.size;

  // Media type mapping
  const MEDIA_TYPES = {
    pdf: 1, doc: 3, docx: 3, ppt: 4, pptx: 4,
    xls: 5, xlsx: 5, png: 7, jpg: 7, jpeg: 7,
    gif: 7, webp: 7, mp3: 9, wav: 9, ogg: 9,
    html: 20, htm: 20, epub: 21,
    mp4: 13, mov: 13, avi: 13, zip: 14, rar: 14,
    '7z': 14, txt: 15, md: 15, csv: 5,
  };
  const CONTENT_TYPES = {
    pdf: 'application/pdf',
    doc: 'application/msword',
    docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ppt: 'application/vnd.ms-powerpoint',
    pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    xls: 'application/vnd.ms-excel',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg',
    gif: 'image/gif', webp: 'image/webp',
    mp3: 'audio/mpeg', wav: 'audio/wav', ogg: 'audio/ogg',
    mp4: 'video/mp4', mov: 'video/quicktime', avi: 'video/x-msvideo',
    zip: 'application/zip', rar: 'application/x-rar-compressed',
    '7z': 'application/x-7z-compressed',
    txt: 'text/plain', md: 'text/markdown', csv: 'text/csv',
    html: 'text/html', htm: 'text/html', epub: 'application/epub+zip',
  };

  const mediaType = MEDIA_TYPES[ext] || 1;
  const contentType = CONTENT_TYPES[ext] || 'application/octet-stream';

  console.error(`📄 ${fileName} (${(fileSize / 1024).toFixed(1)} KB, type=${mediaType})`);

  // Step 1: create_media
  console.error('🔑 Getting COS credentials...');
  const mediaResp = await callIMA('openapi/wiki/v1/create_media', {
    file_name: fileName,
    file_size: fileSize,
    content_type: contentType,
    knowledge_base_id: KB_ID,
    file_ext: ext,
  });
  if (mediaResp.code !== 0) throw new Error(`create_media failed: ${mediaResp.msg}`);
  const d = mediaResp.data;
  const c = d.cos_credential;
  console.error('   Got COS credentials OK');

  // Step 2: Upload to COS
  console.error('☁️  Uploading to COS...');
  const fileContent = fs.readFileSync(FILE_PATH);
  const hostname = `${c.bucket_name}.cos.${c.region}.myqcloud.com`;
  const pathname = `/${c.cos_key}`;
  const keyTime = `${c.start_time};${c.expired_time}`;
  const signKey = hmacSha1(c.secret_key, keyTime);
  const signHeaders = { 'content-length': String(fileContent.length), 'host': hostname };
  const httpString = `put\n${pathname}\n\ncontent-length=${encodeURIComponent(String(fileContent.length))}&host=${encodeURIComponent(hostname)}\n`;
  const stringToSign = `sha1\n${keyTime}\n${sha1(httpString)}\n`;
  const signature = hmacSha1(signKey, stringToSign);

  const authorization = [
    'q-sign-algorithm=sha1', `q-ak=${c.secret_id}`,
    `q-sign-time=${keyTime}`, `q-key-time=${keyTime}`,
    'q-header-list=content-length;host', 'q-url-param-list=',
    `q-signature=${signature}`,
  ].join('&');

  await new Promise((resolve, reject) => {
    const cosReq = https.request({
      hostname, port: 443, path: pathname, method: 'PUT',
      headers: {
        'Content-Type': contentType,
        'Content-Length': fileContent.length,
        'Authorization': authorization,
        'x-cos-security-token': c.token,
      },
      timeout: 300000,
    }, (res) => {
      let body = '';
      res.on('data', (chunk) => (body += chunk));
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          console.error('   COS upload OK');
          resolve();
        } else {
          reject(new Error(`COS ${res.statusCode}: ${body}`));
        }
      });
    });
    cosReq.on('error', reject);
    cosReq.on('timeout', () => { cosReq.destroy(); reject(new Error('COS upload timed out')); });
    cosReq.write(fileContent);
    cosReq.end();
  });

  // Step 3: add_knowledge
  console.error('📚 Adding to knowledge base...');
  const addResp = await callIMA('openapi/wiki/v1/add_knowledge', {
    media_type: mediaType,
    media_id: d.media_id,
    title: FILE_TITLE,
    knowledge_base_id: KB_ID,
    file_info: { cos_key: c.cos_key, file_size: fileSize, file_name: fileName },
  });
  if (addResp.code !== 0) throw new Error(`add_knowledge failed: ${addResp.msg}`);
  console.error(`✅ ${fileName} 已添加到知识库`);
  console.log(JSON.stringify({ media_id: d.media_id, note_id: addResp.data?.media_id }));
}

main().catch((e) => { console.error('❌', e.message); process.exit(1); });
