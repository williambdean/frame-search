import{u as n}from"./hotkeys-Lbk6RHir.js";import{t as i}from"./ansi_up-HmF1kpkv.js";var a=new i;function e(t){try{let r=document.createElement("div");return r.innerHTML=t,(r.textContent||r.innerText||"").split(`
`).map(o=>o.trimEnd()).join(`
`)}catch(r){return n.error("Error parsing HTML content:",r),t}}function c(t){if(!t)return"";try{return e(a.ansi_to_html(t))}catch(r){return n.error("Error converting ANSI to plain text:",r),t}}export{e as n,c as t};
