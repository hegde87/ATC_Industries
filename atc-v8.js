/* Accessible carousel: auto-advance, swipe, keyboard, pause on hover and reduced motion */
(()=>{const carousel=document.querySelector('.atc-carousel');if(!carousel)return;
const slides=[...carousel.querySelectorAll('.atc-slide')],dots=[...carousel.querySelectorAll('.atc-dots button')];
const prev=document.querySelector('.atc-prev'),next=document.querySelector('.atc-next'),toggle=document.querySelector('.atc-toggle');
const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;let current=0,paused=reduced,hover=false,focus=false,timer;
function show(n){current=(n+slides.length)%slides.length;slides.forEach((s,i)=>{s.classList.toggle('is-active',i===current);s.setAttribute('aria-hidden',String(i!==current));s.querySelectorAll('a,button').forEach(el=>{el.tabIndex=i===current?0:-1})});dots.forEach((d,i)=>{d.classList.toggle('is-active',i===current);d.setAttribute('aria-current',String(i===current))})}
function schedule(){clearTimeout(timer);if(!paused&&!hover&&!focus&&!document.hidden){timer=setTimeout(()=>{show(current+1);schedule()},5500)}}
function move(n){show(n);schedule()}
prev?.addEventListener('click',()=>move(current-1));next?.addEventListener('click',()=>move(current+1));dots.forEach((d,i)=>d.addEventListener('click',()=>move(i)));
function updateToggle(){toggle.textContent=paused?'▶ Play':'Ⅱ Pause';toggle.setAttribute('aria-pressed',String(paused));toggle.setAttribute('aria-label',paused?'Play slideshow':'Pause slideshow')}
toggle?.addEventListener('click',()=>{paused=!paused;updateToggle();schedule()});
carousel.addEventListener('mouseenter',()=>{hover=true;schedule()});carousel.addEventListener('mouseleave',()=>{hover=false;schedule()});carousel.addEventListener('focusin',()=>{focus=true;schedule()});carousel.addEventListener('focusout',()=>{focus=false;schedule()});
carousel.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'){e.preventDefault();move(current-1)}if(e.key==='ArrowRight'){e.preventDefault();move(current+1)}});
let startX=null;carousel.addEventListener('touchstart',e=>{startX=e.changedTouches[0].screenX},{passive:true});carousel.addEventListener('touchend',e=>{if(startX===null)return;const dx=e.changedTouches[0].screenX-startX;if(Math.abs(dx)>45)move(current+(dx<0?1:-1));startX=null},{passive:true});
document.addEventListener('visibilitychange',schedule);show(0);updateToggle();schedule();
})();
