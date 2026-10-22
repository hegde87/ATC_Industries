document.addEventListener('DOMContentLoaded',()=>{
 const menu=document.getElementById('menu'),links=document.getElementById('links');
 if(menu&&links){menu.addEventListener('click',()=>{const o=links.classList.toggle('open');menu.setAttribute('aria-expanded',String(o))});links.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{links.classList.remove('open');menu.setAttribute('aria-expanded','false')}))}
 const filterButtons=document.querySelectorAll('[data-filter]'),search=document.getElementById('productSearch');
 function filter(){const active=document.querySelector('[data-filter].active');const cat=active?active.dataset.filter:'all';const q=search?search.value.toLowerCase().trim():'';let count=0;document.querySelectorAll('[data-cat]').forEach(card=>{const show=(cat==='all'||card.dataset.cat===cat)&&card.textContent.toLowerCase().includes(q);card.hidden=!show;if(show)count++});const none=document.getElementById('noProducts');if(none)none.hidden=count!==0}
 filterButtons.forEach(b=>b.addEventListener('click',()=>{filterButtons.forEach(x=>x.classList.toggle('active',x===b));filter()}));
 if(search)search.addEventListener('input',filter);
 const detail=document.getElementById('productDetail');
 if(detail){fetch('products.json').then(r=>r.json()).then(items=>{const id=new URLSearchParams(location.search).get('id');const p=items.find(x=>x.id===id);if(!p){detail.textContent='Product not found. Please return to the catalog.';return}
 const img=document.createElement('img');img.src='assets/'+p.image;img.alt=p.alt;
 const info=document.createElement('div'),pill=document.createElement('span'),h=document.createElement('h2'),desc=document.createElement('p'),spec=document.createElement('div'),btn=document.createElement('a');
 pill.className='pill';pill.textContent=p.category;h.textContent=p.title;desc.textContent=p.description;spec.className='spec';spec.textContent='Product reference: '+p.source+'. Technical specifications, material grades, dimensions and minimum order quantities are available on enquiry.';
 btn.className='btn';btn.href='contact.html?interest='+encodeURIComponent(p.title);btn.textContent='REQUEST A QUOTE →';info.append(pill,h,desc,spec,btn);detail.replaceChildren(img,info);document.title=p.title+' | ATC Industries';
 }).catch(()=>{detail.textContent='To view product details, run the local preview server described in README.md.'})}
 const rfq=document.getElementById('rfq');
 if(rfq){const interest=new URLSearchParams(location.search).get('interest');if(interest){const select=document.getElementById('interest');if(select&&!Array.from(select.options).some(x=>x.value===interest)){const opt=document.createElement('option');opt.value=interest;opt.textContent=interest;select.append(opt)}if(select)select.value=interest}
 rfq.addEventListener('submit',e=>{e.preventDefault();const v=id=>document.getElementById(id)?.value||'';const subject='ATC Industries RFQ - '+v('company');const body='Name: '+v('name')+'\nCompany: '+v('company')+'\nEmail: '+v('email')+'\nPhone: '+v('phone')+'\nInterest: '+v('interest')+'\nEstimated annual quantity: '+v('quantity')+'\n\nRequirements:\n'+v('message');location.href='mailto:atcgoa@gmail.com?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body)})}
});
document.addEventListener('DOMContentLoaded',()=>{const form=document.getElementById('partnerForm');if(!form)return;form.addEventListener('submit',e=>{e.preventDefault();const val=id=>document.getElementById(id).value;const subject='ATC Industries - Business Partner Enquiry - '+val('partnerCompany');const body='Company: '+val('partnerCompany')+'\nContact: '+val('partnerName')+'\nEmail: '+val('partnerEmail')+'\nPhone: '+val('partnerPhone')+'\nRegion: '+val('partnerLocation')+'\nInterest: '+val('partnerType')+'\n\nDetails:\n'+val('partnerDetails');window.location.href='mailto:atcgoa@gmail.com?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body)})});

// ATC V8.8 mobile navigation: keyboard accessible disclosures and Escape-to-close.
document.addEventListener('DOMContentLoaded',()=>{
  const menu=document.getElementById('menu'),nav=document.getElementById('links');
  if(!menu||!nav)return;
  const close=()=>{nav.classList.remove('open');menu.setAttribute('aria-expanded','false');document.body.classList.remove('mobile-nav-open');};
  menu.setAttribute('aria-label','Open navigation menu');
  menu.addEventListener('click',()=>{const opened=nav.classList.contains('open');document.body.classList.toggle('mobile-nav-open',opened);menu.setAttribute('aria-label',opened?'Close navigation menu':'Open navigation menu');});
  nav.querySelectorAll('.mobile-sub-toggle').forEach(btn=>btn.addEventListener('click',()=>{
    const expanded=btn.getAttribute('aria-expanded')==='true';
    btn.setAttribute('aria-expanded',String(!expanded));
    btn.closest('.nav-group').classList.toggle('mobile-expanded',!expanded);
  }));
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open')){close();menu.focus();}});
  document.addEventListener('click',e=>{if(innerWidth<=900&&nav.classList.contains('open')&&!nav.contains(e.target)&&!menu.contains(e.target))close();});
  nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{document.body.classList.remove('mobile-nav-open');}));
  window.addEventListener('resize',()=>{if(innerWidth>900)close();});
});
