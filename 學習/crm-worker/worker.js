const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }

    const url = new URL(request.url);
    const path = url.pathname; // /customers 或 /quotes
    const method = request.method;

    // GET /customers 或 /quotes
    if (method === 'GET' && (path === '/customers' || path === '/quotes')) {
      const data = await env.CRM_DATA.get(path.slice(1));
      return json(data ? JSON.parse(data) : []);
    }

    // POST /customers 或 /quotes → 儲存整份清單
    if (method === 'POST' && (path === '/customers' || path === '/quotes')) {
      const body = await request.json();
      await env.CRM_DATA.put(path.slice(1), JSON.stringify(body));
      return json({ ok: true });
    }

    return json({ error: 'Not found' }, 404);
  },
};
