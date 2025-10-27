import{s as _}from"./chunk-DZLz74EQ.js";import{t as p}from"./react-BcIddLXZ.js";import{n as m}from"./jsx-runtime-DvsdsEjx.js";import{t as x}from"./createLucideIcon-DA8ZBm4D.js";var S=x("chevrons-up-down",[["path",{d:"m7 15 5 5 5-5",key:"1hf1tw"}],["path",{d:"m7 9 5-5 5 5",key:"sgt6xg"}]]),y=_(m(),1),k=_(p(),1),o={};function w(t){let e=(0,y.c)(5),[s,i]=(0,k.useState)(o[t]??!1),r;e[0]===t?r=e[1]:(r=a=>{i(a),o[t]=a},e[0]=t,e[1]=r);let n;return e[2]!==s||e[3]!==r?(n=[s,r],e[2]=s,e[3]=r,e[4]=n):n=e[4],n}function E(t){return t==null||t.data==null||t.data===""}function C(t,e){return`data:${e};base64,${t}`}function g(t){return window.atob(t)}function I(t){return t.startsWith("data:")&&t.includes(";base64,")}function v(t){return t.split(",")[1]}function b(t){return Uint8Array.from(t,e=>e.charCodeAt(0))}function O(t){return(t.buffers??[]).map(e=>{let s=b(g(e));return new DataView(s.buffer)})}var u=function(t,e){return Object.defineProperty?Object.defineProperty(t,"raw",{value:e}):t.raw=e,t},l;(function(t){t[t.EOS=0]="EOS",t[t.Text=1]="Text",t[t.Incomplete=2]="Incomplete",t[t.ESC=3]="ESC",t[t.Unknown=4]="Unknown",t[t.SGR=5]="SGR",t[t.OSCURL=6]="OSCURL"})(l||(l={}));var $=class{constructor(){this.VERSION="6.0.6",this.setup_palettes(),this._use_classes=!1,this.bold=!1,this.faint=!1,this.italic=!1,this.underline=!1,this.fg=this.bg=null,this._buffer="",this._url_allowlist={http:1,https:1},this._escape_html=!0,this.boldStyle="font-weight:bold",this.faintStyle="opacity:0.7",this.italicStyle="font-style:italic",this.underlineStyle="text-decoration:underline"}set use_classes(t){this._use_classes=t}get use_classes(){return this._use_classes}set url_allowlist(t){this._url_allowlist=t}get url_allowlist(){return this._url_allowlist}set escape_html(t){this._escape_html=t}get escape_html(){return this._escape_html}set boldStyle(t){this._boldStyle=t}get boldStyle(){return this._boldStyle}set faintStyle(t){this._faintStyle=t}get faintStyle(){return this._faintStyle}set italicStyle(t){this._italicStyle=t}get italicStyle(){return this._italicStyle}set underlineStyle(t){this._underlineStyle=t}get underlineStyle(){return this._underlineStyle}setup_palettes(){this.ansi_colors=[[{rgb:[0,0,0],class_name:"ansi-black"},{rgb:[187,0,0],class_name:"ansi-red"},{rgb:[0,187,0],class_name:"ansi-green"},{rgb:[187,187,0],class_name:"ansi-yellow"},{rgb:[0,0,187],class_name:"ansi-blue"},{rgb:[187,0,187],class_name:"ansi-magenta"},{rgb:[0,187,187],class_name:"ansi-cyan"},{rgb:[255,255,255],class_name:"ansi-white"}],[{rgb:[85,85,85],class_name:"ansi-bright-black"},{rgb:[255,85,85],class_name:"ansi-bright-red"},{rgb:[0,255,0],class_name:"ansi-bright-green"},{rgb:[255,255,85],class_name:"ansi-bright-yellow"},{rgb:[85,85,255],class_name:"ansi-bright-blue"},{rgb:[255,85,255],class_name:"ansi-bright-magenta"},{rgb:[85,255,255],class_name:"ansi-bright-cyan"},{rgb:[255,255,255],class_name:"ansi-bright-white"}]],this.palette_256=[],this.ansi_colors.forEach(s=>{s.forEach(i=>{this.palette_256.push(i)})});let t=[0,95,135,175,215,255];for(let s=0;s<6;++s)for(let i=0;i<6;++i)for(let r=0;r<6;++r){let n={rgb:[t[s],t[i],t[r]],class_name:"truecolor"};this.palette_256.push(n)}let e=8;for(let s=0;s<24;++s,e+=10){let i={rgb:[e,e,e],class_name:"truecolor"};this.palette_256.push(i)}}escape_txt_for_html(t){return this._escape_html?t.replace(/[&<>"']/gm,e=>{if(e==="&")return"&amp;";if(e==="<")return"&lt;";if(e===">")return"&gt;";if(e==='"')return"&quot;";if(e==="'")return"&#x27;"}):t}append_buffer(t){this._buffer+=t}get_next_packet(){var t={kind:l.EOS,text:"",url:""},e=this._buffer.length;if(e==0)return t;var s=this._buffer.indexOf("\x1B");if(s==-1)return t.kind=l.Text,t.text=this._buffer,this._buffer="",t;if(s>0)return t.kind=l.Text,t.text=this._buffer.slice(0,s),this._buffer=this._buffer.slice(s),t;if(s==0){if(e<3)return t.kind=l.Incomplete,t;var i=this._buffer.charAt(1);if(i!="["&&i!="]"&&i!="(")return t.kind=l.ESC,t.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),t;if(i=="["){this._csi_regex||(this._csi_regex=d(R||(R=u([`
                        ^                           # beginning of line
                                                    #
                                                    # First attempt
                        (?:                         # legal sequence
                          \x1B[                      # CSI
                          ([<-?]?)              # private-mode char
                          ([d;]*)                    # any digits or semicolons
                          ([ -/]?               # an intermediate modifier
                          [@-~])                # the command
                        )
                        |                           # alternate (second attempt)
                        (?:                         # illegal sequence
                          \x1B[                      # CSI
                          [ -~]*                # anything legal
                          ([\0-:])              # anything illegal
                        )
                    `],[`
                        ^                           # beginning of line
                                                    #
                                                    # First attempt
                        (?:                         # legal sequence
                          \\x1b\\[                      # CSI
                          ([\\x3c-\\x3f]?)              # private-mode char
                          ([\\d;]*)                    # any digits or semicolons
                          ([\\x20-\\x2f]?               # an intermediate modifier
                          [\\x40-\\x7e])                # the command
                        )
                        |                           # alternate (second attempt)
                        (?:                         # illegal sequence
                          \\x1b\\[                      # CSI
                          [\\x20-\\x7e]*                # anything legal
                          ([\\x00-\\x1f:])              # anything illegal
                        )
                    `]))));let n=this._buffer.match(this._csi_regex);if(n===null)return t.kind=l.Incomplete,t;if(n[4])return t.kind=l.ESC,t.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),t;n[1]!=""||n[3]!="m"?t.kind=l.Unknown:t.kind=l.SGR,t.text=n[2];var r=n[0].length;return this._buffer=this._buffer.slice(r),t}else if(i=="]"){if(e<4)return t.kind=l.Incomplete,t;if(this._buffer.charAt(2)!="8"||this._buffer.charAt(3)!=";")return t.kind=l.ESC,t.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),t;this._osc_st||(this._osc_st=B(T||(T=u([`
                        (?:                         # legal sequence
                          (\x1B\\)                    # ESC                           |                           # alternate
                          (\x07)                      # BEL (what xterm did)
                        )
                        |                           # alternate (second attempt)
                        (                           # illegal sequence
                          [\0-]                 # anything illegal
                          |                           # alternate
                          [\b-]                 # anything illegal
                          |                           # alternate
                          [-]                 # anything illegal
                        )
                    `],[`
                        (?:                         # legal sequence
                          (\\x1b\\\\)                    # ESC \\
                          |                           # alternate
                          (\\x07)                      # BEL (what xterm did)
                        )
                        |                           # alternate (second attempt)
                        (                           # illegal sequence
                          [\\x00-\\x06]                 # anything illegal
                          |                           # alternate
                          [\\x08-\\x1a]                 # anything illegal
                          |                           # alternate
                          [\\x1c-\\x1f]                 # anything illegal
                        )
                    `])))),this._osc_st.lastIndex=0;{let h=this._osc_st.exec(this._buffer);if(h===null)return t.kind=l.Incomplete,t;if(h[3])return t.kind=l.ESC,t.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),t}{let h=this._osc_st.exec(this._buffer);if(h===null)return t.kind=l.Incomplete,t;if(h[3])return t.kind=l.ESC,t.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),t}this._osc_regex||(this._osc_regex=d(L||(L=u([`
                        ^                           # beginning of line
                                                    #
                        \x1B]8;                    # OSC Hyperlink
                        [ -:<-~]*       # params (excluding ;)
                        ;                           # end of params
                        ([!-~]{0,512})        # URL capture
                        (?:                         # ST
                          (?:\x1B\\)                  # ESC                           |                           # alternate
                          (?:\x07)                    # BEL (what xterm did)
                        )
                        ([ -~]+)              # TEXT capture
                        \x1B]8;;                   # OSC Hyperlink End
                        (?:                         # ST
                          (?:\x1B\\)                  # ESC                           |                           # alternate
                          (?:\x07)                    # BEL (what xterm did)
                        )
                    `],[`
                        ^                           # beginning of line
                                                    #
                        \\x1b\\]8;                    # OSC Hyperlink
                        [\\x20-\\x3a\\x3c-\\x7e]*       # params (excluding ;)
                        ;                           # end of params
                        ([\\x21-\\x7e]{0,512})        # URL capture
                        (?:                         # ST
                          (?:\\x1b\\\\)                  # ESC \\
                          |                           # alternate
                          (?:\\x07)                    # BEL (what xterm did)
                        )
                        ([\\x20-\\x7e]+)              # TEXT capture
                        \\x1b\\]8;;                   # OSC Hyperlink End
                        (?:                         # ST
                          (?:\\x1b\\\\)                  # ESC \\
                          |                           # alternate
                          (?:\\x07)                    # BEL (what xterm did)
                        )
                    `]))));let n=this._buffer.match(this._osc_regex);if(n===null)return t.kind=l.ESC,t.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),t;t.kind=l.OSCURL,t.url=n[1],t.text=n[2];var r=n[0].length;return this._buffer=this._buffer.slice(r),t}else if(i=="(")return t.kind=l.Unknown,this._buffer=this._buffer.slice(3),t}}ansi_to_html(t){this.append_buffer(t);for(var e=[];;){var s=this.get_next_packet();if(s.kind==l.EOS||s.kind==l.Incomplete)break;s.kind==l.ESC||s.kind==l.Unknown||(s.kind==l.Text?e.push(this.transform_to_html(this.with_state(s))):s.kind==l.SGR?this.process_ansi(s):s.kind==l.OSCURL&&e.push(this.process_hyperlink(s)))}return e.join("")}with_state(t){return{bold:this.bold,faint:this.faint,italic:this.italic,underline:this.underline,fg:this.fg,bg:this.bg,text:t.text}}process_ansi(t){let e=t.text.split(";");for(;e.length>0;){let s=e.shift(),i=parseInt(s,10);if(isNaN(i)||i===0)this.fg=null,this.bg=null,this.bold=!1,this.faint=!1,this.italic=!1,this.underline=!1;else if(i===1)this.bold=!0;else if(i===2)this.faint=!0;else if(i===3)this.italic=!0;else if(i===4)this.underline=!0;else if(i===21)this.bold=!1;else if(i===22)this.faint=!1,this.bold=!1;else if(i===23)this.italic=!1;else if(i===24)this.underline=!1;else if(i===39)this.fg=null;else if(i===49)this.bg=null;else if(i>=30&&i<38)this.fg=this.ansi_colors[0][i-30];else if(i>=40&&i<48)this.bg=this.ansi_colors[0][i-40];else if(i>=90&&i<98)this.fg=this.ansi_colors[1][i-90];else if(i>=100&&i<108)this.bg=this.ansi_colors[1][i-100];else if((i===38||i===48)&&e.length>0){let r=i===38,n=e.shift();if(n==="5"&&e.length>0){let a=parseInt(e.shift(),10);a>=0&&a<=255&&(r?this.fg=this.palette_256[a]:this.bg=this.palette_256[a])}if(n==="2"&&e.length>2){let a=parseInt(e.shift(),10),h=parseInt(e.shift(),10),f=parseInt(e.shift(),10);if(a>=0&&a<=255&&h>=0&&h<=255&&f>=0&&f<=255){let c={rgb:[a,h,f],class_name:"truecolor"};r?this.fg=c:this.bg=c}}}}}transform_to_html(t){let e=t.text;if(e.length===0||(e=this.escape_txt_for_html(e),!t.bold&&!t.italic&&!t.faint&&!t.underline&&t.fg===null&&t.bg===null))return e;let s=[],i=[],r=t.fg,n=t.bg;t.bold&&s.push(this._boldStyle),t.faint&&s.push(this._faintStyle),t.italic&&s.push(this._italicStyle),t.underline&&s.push(this._underlineStyle),this._use_classes?(r&&(r.class_name==="truecolor"?s.push(`color:rgb(${r.rgb.join(",")})`):i.push(`${r.class_name}-fg`)),n&&(n.class_name==="truecolor"?s.push(`background-color:rgb(${n.rgb.join(",")})`):i.push(`${n.class_name}-bg`))):(r&&s.push(`color:rgb(${r.rgb.join(",")})`),n&&s.push(`background-color:rgb(${n.rgb})`));let a="",h="";return i.length&&(a=` class="${i.join(" ")}"`),s.length&&(h=` style="${s.join(";")}"`),`<span${h}${a}>${e}</span>`}process_hyperlink(t){let e=t.url.split(":");return e.length<1||!this._url_allowlist[e[0]]?"":`<a href="${this.escape_txt_for_html(t.url)}">${this.escape_txt_for_html(t.text)}</a>`}};function d(t,...e){let s=t.raw[0].replace(/^\s+|\s+\n|\s*#[\s\S]*?\n|\n/gm,"");return new RegExp(s)}function B(t,...e){let s=t.raw[0].replace(/^\s+|\s+\n|\s*#[\s\S]*?\n|\n/gm,"");return new RegExp(s,"g")}var R,T,L;export{I as a,E as c,v as i,w as l,C as n,O as o,b as r,g as s,$ as t,S as u};
