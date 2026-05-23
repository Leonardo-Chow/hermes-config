#!/usr/bin/env node

/**
 * 微博热搜获取脚本
 * 数据来源：微博网页端公开接口 weibo.com/ajax/side/hotSearch
 * 
 * 用法：
 *   node scripts/weibo.js       # 默认获取50条
 *   node scripts/weibo.js 20    # 获取前20条
 */

const https = require('https');

// 获取命令行参数
const limit = parseInt(process.argv[2]) || 50;

// 请求选项
const options = {
  hostname: 'weibo.com',
  path: '/ajax/side/hotSearch',
  method: 'GET',
  headers: {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://weibo.com/',
    'X-Requested-With': 'XMLHttpRequest'
  }
};

// 发送请求
const req = https.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    try {
      const json = JSON.parse(data);
      
      if (json.ok !== 1) {
        console.error('请求失败:', json);
        process.exit(1);
      }

      const realtime = json.data?.realtime || [];
      const items = realtime.slice(0, limit);

      // 输出格式化结果
      console.log(`\n🔥 微博热搜 TOP ${items.length}\n`);
      console.log('─'.repeat(80));
      console.log(`${'排名'.padEnd(4)} | ${'标题'.padEnd(40)} | ${'热度'.padEnd(10)} | 标签`);
      console.log('─'.repeat(80));

      items.forEach((item, index) => {
        const rank = (index + 1).toString().padEnd(4);
        const title = (item.word || '').substring(0, 38).padEnd(40);
        const hot = formatNumber(item.num || 0).padEnd(10);
        const label = item.label_name || '';
        
        console.log(`${rank} | ${title} | ${hot} | ${label}`);
      });

      console.log('─'.repeat(80));
      console.log(`\n📊 共 ${items.length} 条热搜\n`);

      // 输出 JSON 格式（供其他程序使用）
      if (process.argv.includes('--json')) {
        console.log('\n--- JSON OUTPUT ---');
        console.log(JSON.stringify(items, null, 2));
      }

    } catch (error) {
      console.error('解析响应失败:', error.message);
      console.error('原始响应:', data.substring(0, 500));
      process.exit(1);
    }
  });
});

req.on('error', (error) => {
  console.error('请求错误:', error.message);
  process.exit(1);
});

req.setTimeout(10000, () => {
  console.error('请求超时');
  req.destroy();
  process.exit(1);
});

req.end();

// 格式化数字
function formatNumber(num) {
  if (num >= 100000000) {
    return (num / 100000000).toFixed(1) + '亿';
  } else if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万';
  } else {
    return num.toString();
  }
}
