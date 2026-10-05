// Server-side OpenAI-compatible transport. No secrets are included in UI status.
export function normalizeBaseUrl(value){
  let url;try{url=new URL(value);}catch{throw new Error('AI 服务地址必须是完整的 HTTP(S) Base URL。');}
  if(!['http:','https:'].includes(url.protocol)||url.username||url.password||url.search||url.hash)throw new Error('AI Base URL 不能包含密钥、账号、查询参数或片段。');
  if(/\/(chat\/completions|responses)\/?$/.test(url.pathname))throw new Error('请填写 Base URL（如 /v1），不要填写具体请求端点。');
  const pathname=url.pathname.replace(/\/+$/,'')||'/v1';
  return url.origin+pathname;
}

function responseInput(messages){
  return messages.flatMap(m=>{
    if(m.role==='tool')return [{type:'function_call_output',call_id:m.tool_call_id,output:String(m.content)}];
    if(m.role==='assistant'&&m.responseItems)return m.responseItems;
    const content=typeof m.content==='string'?[{type:m.role==='assistant'?'output_text':'input_text',text:m.content}]:Array.isArray(m.content)?m.content.map(c=>{
      if(c.type==='text')return {type:'input_text',text:c.text};
      if(c.type==='image_url')return {type:'input_image',image_url:c.image_url.url,...(c.image_url.detail?{detail:c.image_url.detail}:{})};
      throw new Error('当前 AI 输入仅支持文字和图片。');
    }):[];
    return [...(content.length?[{role:m.role,content}]:[]),...(m.tool_calls||[]).map(c=>({type:'function_call',call_id:c.id,name:c.function.name,arguments:c.function.arguments}))];
  });
}

export function createOpenAiClient({baseUrl,apiKey='',apiStyle='chat-completions',fetchImpl=fetch}){
  const base=normalizeBaseUrl(baseUrl);
  if(!['chat-completions','responses'].includes(apiStyle))throw new Error('AI API 协议必须为 chat-completions 或 responses。');
  async function request(endpoint,body,signal){
    const key=typeof apiKey==='function'?await apiKey():apiKey;
    let res;try{res=await fetchImpl(base+'/'+endpoint,{method:body?'POST':'GET',redirect:'manual',headers:{'Content-Type':'application/json',...(key?{Authorization:'Bearer '+key}:{})},...(body?{body:JSON.stringify(body)}:{}),signal:signal||AbortSignal.timeout(15000)});}
    catch(e){throw new Error(e.name==='TimeoutError'||e.name==='AbortError'?'AI 请求超时；已执行的动作保留，可在记录中撤销。':'无法连接 AI 服务。手动操作仍可使用。');}
    if(!res.ok)throw new Error(`AI 服务返回 HTTP ${res.status}。请检查协议、模型、密钥与服务权限。`);
    try{return await res.json();}catch{throw new Error('AI 服务未返回有效 JSON。');}
  }
  return {
    async listModels(signal){const data=await request('models',null,signal);return (data.data||[]).map(m=>m.id).filter(id=>typeof id==='string');},
    async complete({model,messages,tools=[],signal}){
      if(!model)throw new Error('请先配置 OPENAI_MODEL。');
      if(apiStyle==='chat-completions'){
        const data=await request('chat/completions',{model,messages,tools,tool_choice:'auto',stream:false,max_tokens:5000},signal);
        const m=data.choices?.[0]?.message;if(!m||m.role!=='assistant')throw new Error('AI 服务未返回有效助手消息。');return m;
      }
      const data=await request('responses',{model,input:responseInput(messages),tools:tools.map(t=>({type:'function',...t.function,strict:false})),tool_choice:'auto',stream:false,store:false,max_output_tokens:5000,include:['reasoning.encrypted_content']},signal);
      if(!Array.isArray(data.output)||data.status&&data.status!=='completed')throw new Error('AI 服务未返回完整 Responses 输出。');
      return {role:'assistant',content:data.output.filter(o=>o.type==='message').flatMap(o=>o.content||[]).filter(c=>c.type==='output_text').map(c=>c.text).join('\n'),tool_calls:data.output.filter(o=>o.type==='function_call').map(o=>({id:o.call_id,type:'function',function:{name:o.name,arguments:o.arguments}})),responseItems:data.output};
    }
  };
}
