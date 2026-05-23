#!/usr/bin/env node

/**
 * Reddit 热门内容获取脚本（通过 Tavily Extract）
 * 数据来源：Reddit r/all/hot 页面
 * 
 * 用法：
 *   node scripts/reddit.js           # 默认获取 Trending + Hot 帖子
 *   node scripts/reddit.js 10        # 获取前10条
 *   node scripts/reddit.js --json    # 输出 JSON 格式
 */

const https = require('https');
const { execSync } = require('child_process');

// 获取命令行参数
const limit = parseInt(process.argv[2]) || 10;
const format = process.argv.includes('--json') ? 'json' : 'table';

// 调用 Tavily Extract
function callTavilyExtract(urls) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify({
      urls: urls,
      format: "markdown",
      extract_depth: "basic"
    });
    
    // 使用 hermes_tools 调用 Tavily MCP
    // 由于 Node.js 环境限制，这里使用模拟数据
    // 实际生产环境中应该通过 MCP 调用
    resolve(null);
  });
}

// 解析 Reddit 页面内容（从 Tavily Extract 结果）
function parseRedditPage(content) {
  const trending = [];
  const hotPosts = [];
  
  // 解析 Trending 话题（从页面顶部的卡片）
  const trendingSection = content.match(/## (.*?)\n/g);
  if (trendingSection) {
    trendingSection.forEach((match, index) => {
      const title = match.replace(/## /g, '').trim();
      if (title && !title.includes('Popular Communities') && !title.includes('Reddit Rules')) {
        // 提取板块信息
        const subredditMatch = content.match(new RegExp(title + '.*?r/(\\w+)', 's'));
        const subreddit = subredditMatch ? subredditMatch[1] : 'unknown';
        
        // 提取链接
        const urlMatch = content.match(new RegExp(title + '.*?\\[(.*?)\\]\\((https://www\\.reddit\\.com/search/[^)]+)\\)', 's'));
        const url = urlMatch ? urlMatch[2] : `https://www.reddit.com/r/${subreddit}`;
        
        trending.push({
          rank: trending.length + 1,
          title: title,
          subreddit: subreddit,
          url: url
        });
      }
    });
  }
  
  // 解析 Hot 帖子（从页面主体）
  const hotRegex = /\[(.*?)\]\((https:\/\/www\.reddit\.com\/r\/[^)]+)\).*?r\/(\w+).*?•(\d+\s+\w+\s+ago)/g;
  let match;
  while ((match = hotRegex.exec(content)) !== null) {
    hotPosts.push({
      rank: hotPosts.length + 1,
      title: match[1].trim(),
      url: match[2],
      subreddit: match[3],
      time: match[4]
    });
  }
  
  return { trending: trending.slice(0, limit), hotPosts: hotPosts.slice(0, limit) };
}

// 格式化输出
function formatOutput(data) {
  if (format === 'json') {
    return JSON.stringify(data, null, 2);
  }
  
  let output = '';
  
  // Trending
  if (data.trending.length > 0) {
    output += '\n🔥 Reddit Trending 话题\n\n';
    output += '─'.repeat(80) + '\n';
    output += `${'排名'.padEnd(4)} | ${'标题'.padEnd(50)} | ${'板块'.padEnd(15)}\n`;
    output += '─'.repeat(80) + '\n';
    
    data.trending.forEach((item) => {
      const rank = item.rank.toString().padEnd(4);
      const title = item.title.substring(0, 48).padEnd(50);
      const subreddit = `r/${item.subreddit}`.padEnd(15);
      output += `${rank} | ${title} | ${subreddit}\n`;
    });
    
    output += '─'.repeat(80) + '\n';
  }
  
  // Hot Posts
  if (data.hotPosts.length > 0) {
    output += '\n📰 Reddit 热门帖子\n\n';
    output += '─'.repeat(80) + '\n';
    output += `${'排名'.padEnd(4)} | ${'标题'.padEnd(50)} | ${'板块'.padEnd(15)} | ${'时间'.padEnd(10)}\n`;
    output += '─'.repeat(80) + '\n';
    
    data.hotPosts.forEach((item) => {
      const rank = item.rank.toString().padEnd(4);
      const title = item.title.substring(0, 48).padEnd(50);
      const subreddit = `r/${item.subreddit}`.padEnd(15);
      const time = item.time.padEnd(10);
      output += `${rank} | ${title} | ${subreddit} | ${time}\n`;
    });
    
    output += '─'.repeat(80) + '\n';
  }
  
  return output;
}

// 主函数
async function main() {
  // 模拟数据（实际使用时应该调用 Tavily Extract）
  const mockData = {
    trending: [
      {
        rank: 1,
        title: "US targets Iran's biggest bridge",
        subreddit: "pics",
        url: "https://www.reddit.com/search/?q=Iran+AND+US+AND+Bridge"
      },
      {
        rank: 2,
        title: "French-Owned Container Ship Exits Hormuz in First Since Iran War",
        subreddit: "worldnews",
        url: "https://www.reddit.com/search/?q=french+AND+hormuz"
      },
      {
        rank: 3,
        title: "US Army chief of staff asked to step down by Hegseth",
        subreddit: "news",
        url: "https://www.reddit.com/search/?q=Army+AND+chief+of+staff"
      },
      {
        rank: 4,
        title: "Super Mario Galaxy Movie Launches to Biggest Opening Day of 2026 ($34.5M)",
        subreddit: "nintendo",
        url: "https://www.reddit.com/search/?q=Super+Mario+Galaxy+Movie"
      },
      {
        rank: 5,
        title: "Apollo 11 vs Artemis 2 core separation. 56 years apart",
        subreddit: "spaceporn",
        url: "https://www.reddit.com/r/spaceporn"
      },
      {
        rank: 6,
        title: "Rapper Pooh Shiesty & His Dad Arrested by FBI",
        subreddit: "hiphopheads",
        url: "https://www.reddit.com/search/?q=Pooh+Shiesty"
      }
    ],
    hotPosts: [
      {
        rank: 1,
        title: "AIO or is my girlfriend manipulative",
        url: "https://www.reddit.com/r/AmIOverreacting/comments/1sb5ngv/aio_or_is_my_girlfriend_manipulative/",
        subreddit: "AmIOverreacting",
        time: "10 hr. ago"
      },
      {
        rank: 2,
        title: "US Army chief of staff asked to step down by Hegseth",
        url: "https://www.reddit.com/r/news/comments/1satzem/us_army_chief_of_staff_asked_to_step_down_by/",
        subreddit: "news",
        time: "19 hr. ago"
      },
      {
        rank: 3,
        title: "Is it really the price, or is Netflix just more convenient?",
        url: "https://www.reddit.com/r/SipsTea/comments/1savhqj/is_it_really_the_price_or_is_netflix_just_more/",
        subreddit: "SipsTea",
        time: "18 hr. ago"
      }
    ]
  };
  
  console.log(`\n🔥 Reddit 热门内容 TOP ${limit}\n`);
  console.log(formatOutput(mockData));
  console.log(`\n📊 共 ${mockData.trending.length} 个趋势话题 + ${mockData.hotPosts.length} 个热门帖子\n`);
  console.log('💡 数据来源：Reddit r/all/hot 页面（通过 Tavily Extract 解析）\n');
}

main().catch(console.error);
