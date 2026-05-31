#!/usr/bin/env node
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

const API = 'https://gis-crm-api.fooicebo.workers.dev';

// ===== API 工具函式 =====
async function getList(type) {
  const res = await fetch(`${API}/${type}`);
  return res.json();
}

async function saveList(type, data) {
  await fetch(`${API}/${type}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

// ===== MCP Server =====
const server = new McpServer({
  name: 'gis-crm',
  version: '1.0.0',
});

// ─── 客戶工具 ───────────────────────────────────────────

server.tool(
  'list_customers',
  '列出所有客戶資料',
  {},
  async () => {
    const customers = await getList('customers');
    if (!customers.length) return { content: [{ type: 'text', text: '目前無客戶資料。' }] };
    const text = customers.map(c =>
      `【${c.company}】\n  聯絡人：${c.name || '-'} ${c.title || ''}\n  電話：${c.phone || '-'} ｜ 手機：${c.mobile || '-'}\n  Email：${c.email || '-'}\n  地址：${c.address || '-'}\n  網址：${c.website || '-'}\n  統編：${c.taxid || '-'}\n  備註：${c.note || '-'}`
    ).join('\n\n');
    return { content: [{ type: 'text', text }] };
  }
);

server.tool(
  'add_customer',
  '新增一筆客戶資料到 CRM',
  {
    company:  z.string().describe('公司名稱（必填）'),
    name:     z.string().optional().describe('聯絡人姓名'),
    title:    z.string().optional().describe('職稱'),
    phone:    z.string().optional().describe('電話'),
    mobile:   z.string().optional().describe('手機'),
    email:    z.string().optional().describe('Email'),
    address:  z.string().optional().describe('地址'),
    website:  z.string().optional().describe('公司網址'),
    taxid:    z.string().optional().describe('統一編號'),
    note:     z.string().optional().describe('備註'),
  },
  async (args) => {
    const customers = await getList('customers');
    const exists = customers.find(c => c.company === args.company);
    if (exists) return { content: [{ type: 'text', text: `⚠️ 客戶「${args.company}」已存在，請使用 update_customer 更新。` }] };
    const newCustomer = { id: Date.now().toString(), ...args };
    customers.unshift(newCustomer);
    await saveList('customers', customers);
    return { content: [{ type: 'text', text: `✅ 已新增客戶：${args.company}` }] };
  }
);

server.tool(
  'update_customer',
  '更新已有客戶的資料（依公司名稱搜尋）',
  {
    company:  z.string().describe('要更新的公司名稱'),
    name:     z.string().optional(),
    title:    z.string().optional(),
    phone:    z.string().optional(),
    mobile:   z.string().optional(),
    email:    z.string().optional(),
    address:  z.string().optional(),
    website:  z.string().optional(),
    taxid:    z.string().optional(),
    note:     z.string().optional(),
  },
  async (args) => {
    const customers = await getList('customers');
    const idx = customers.findIndex(c =>
      c.company.includes(args.company) || args.company.includes(c.company)
    );
    if (idx === -1) return { content: [{ type: 'text', text: `❌ 找不到客戶「${args.company}」` }] };
    customers[idx] = { ...customers[idx], ...args };
    await saveList('customers', customers);
    return { content: [{ type: 'text', text: `✅ 已更新客戶：${customers[idx].company}` }] };
  }
);

server.tool(
  'delete_customer',
  '刪除客戶資料',
  { company: z.string().describe('要刪除的公司名稱') },
  async ({ company }) => {
    const customers = await getList('customers');
    const filtered = customers.filter(c => !c.company.includes(company));
    if (filtered.length === customers.length) return { content: [{ type: 'text', text: `❌ 找不到客戶「${company}」` }] };
    await saveList('customers', filtered);
    return { content: [{ type: 'text', text: `✅ 已刪除客戶：${company}` }] };
  }
);

// ─── 報價單工具 ─────────────────────────────────────────

server.tool(
  'list_quotes',
  '列出所有報價單',
  {},
  async () => {
    const [quotes, customers] = await Promise.all([getList('quotes'), getList('customers')]);
    if (!quotes.length) return { content: [{ type: 'text', text: '目前無報價單。' }] };
    const text = quotes.map(q => {
      const c = customers.find(x => x.id === q.customerId);
      const sub = (q.items || []).reduce((s, i) => s + i.qty * i.price, 0);
      const items = (q.items || []).map(i => `    - ${i.name} × ${i.qty} = $${(i.qty * i.price).toLocaleString()}`).join('\n');
      return `【${c?.company || '未知'}】${q.title || ''}\n  日期：${q.date}\n  品項：\n${items}\n  含稅總計：$${Math.round(sub * 1.05).toLocaleString()}\n  備註：${q.note || '-'}`;
    }).join('\n\n');
    return { content: [{ type: 'text', text }] };
  }
);

server.tool(
  'add_quote',
  '新增一筆報價單到 CRM',
  {
    company: z.string().describe('客戶公司名稱'),
    title:   z.string().optional().describe('報價說明，例如：衛浴採購'),
    date:    z.string().optional().describe('報價日期 YYYY-MM-DD，預設今日'),
    items:   z.array(z.object({
      name:  z.string().describe('品名'),
      qty:   z.number().describe('數量'),
      price: z.number().describe('單價'),
    })).describe('品項清單'),
    note:    z.string().optional().describe('備註'),
  },
  async (args) => {
    const [quotes, customers] = await Promise.all([getList('quotes'), getList('customers')]);
    const customer = customers.find(c => c.company.includes(args.company) || args.company.includes(c.company));
    if (!customer) return { content: [{ type: 'text', text: `❌ 找不到客戶「${args.company}」，請先新增客戶。` }] };
    const sub = args.items.reduce((s, i) => s + i.qty * i.price, 0);
    const newQuote = {
      id: Date.now().toString(),
      customerId: customer.id,
      title: args.title || '',
      date: args.date || new Date().toISOString().slice(0, 10),
      items: args.items,
      note: args.note || '',
    };
    quotes.unshift(newQuote);
    await saveList('quotes', quotes);
    return { content: [{ type: 'text', text:
      `✅ 已新增報價單\n客戶：${customer.company}\n說明：${args.title || '-'}\n含稅總計：$${Math.round(sub * 1.05).toLocaleString()}`
    }] };
  }
);

server.tool(
  'search_customer',
  '搜尋客戶（依名稱、電話、Email）',
  { keyword: z.string().describe('搜尋關鍵字') },
  async ({ keyword }) => {
    const customers = await getList('customers');
    const kw = keyword.toLowerCase();
    const found = customers.filter(c =>
      (c.company + c.name + c.phone + c.mobile + c.email).toLowerCase().includes(kw)
    );
    if (!found.length) return { content: [{ type: 'text', text: `找不到符合「${keyword}」的客戶。` }] };
    const text = found.map(c =>
      `【${c.company}】${c.name || ''} ${c.title || ''} ｜ ${c.phone || ''} ｜ ${c.email || ''}`
    ).join('\n');
    return { content: [{ type: 'text', text }] };
  }
);

// ===== 啟動 =====
const transport = new StdioServerTransport();
await server.connect(transport);
