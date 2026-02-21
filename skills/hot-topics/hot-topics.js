/**
 * Hot Topics Collector Skill
 * 
 * 收集各大平台热点话题
 */

export default {
  name: "hot-topics",
  description: "收集微博、知乎、百度等平台热点话题",
  parameters: {
    type: "object",
    properties: {
      platforms: {
        type: "array",
        description: "要收集的平台列表",
        items: {
          type: "string",
          enum: ["weibo", "zhihu", "baidu"],
        },
        default: ["weibo", "zhihu", "baidu"],
      },
    },
  },

  async run(params) {
    const { platforms = ["weibo", "zhihu", "baidu"] } = params;
    
    const results = {
      timestamp: new Date().toISOString(),
      platforms: {},
    };

    // 收集各平台热点
    if (platforms.includes("weibo")) {
      results.platforms.weibo = await this.fetchWeibo();
    }
    
    if (platforms.includes("zhihu")) {
      results.platforms.zhihu = await this.fetchZhihu();
    }
    
    if (platforms.includes("baidu")) {
      results.platforms.baidu = await this.fetchBaidu();
    }

    return results;
  },

  async fetchWeibo() {
    try {
      const response = await fetch("https://weibo.com/ajax/statuses/hot", {
        method: "GET",
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
          "Referer": "https://weibo.com",
        },
      });
      
      const data = await response.json();
      
      if (data.ok === 1 && data.data) {
        const hotList = data.data.filter(item => item.word); // 只保留有内容的
        return {
          success: true,
          count: hotList.length,
          topics: hotList.slice(0, 20).map(item => ({
            rank: item.rank,
            word: item.word,
            rawUrl: item.rawUrl,
          })),
        };
      }
      
      return { success: false, error: "无法获取微博热搜" };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async fetchZhihu() {
    try {
      const response = await fetch("https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=20", {
        method: "GET",
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
      });
      
      const data = await response.json();
      
      if (data.data) {
        return {
          success: true,
          count: data.data.length,
          topics: data.data.slice(0, 20).map(item => ({
            title: item.target.title,
            excerpt: item.target.excerpt,
            url: item.target.url,
            heat: item.detail_text,
          })),
        };
      }
      
      return { success: false, error: "无法获取知乎热榜" };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async fetchBaidu() {
    try {
      // 尝试多个可能的端点
      const response = await fetch("https://top.baidu.com/api/recommend", {
        method: "GET",
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
      });
      
      const data = await response.json();
      
      if (data.code === 0 && data.result) {
        const items = data.result.data || [];
        return {
          success: true,
          count: items.length,
          topics: items.slice(0, 20).map(item => ({
            rank: item.index,
            title: item.content,
            heat: item.hotScore,
          })),
        };
      }
      
      return { success: false, error: "无法获取百度热搜" };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },
};
