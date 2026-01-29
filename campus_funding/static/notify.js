// Simple toast/slider notification system for the app
function makeToast(message, type = 'success', duration = 4000){
  const wrapId = 'toast-wrap';
  let wrap = document.getElementById(wrapId);
  if(!wrap){ wrap = document.createElement('div'); wrap.id = wrapId; wrap.className = 'toast-wrap'; document.body.appendChild(wrap); }

  const toast = document.createElement('div');
  toast.className = 'toast ' + (type === 'error' ? 'error' : 'success');
  toast.style.setProperty('--dur', (duration/1000) + 's');
  toast.style.setProperty('--bar', type === 'error' ? 'linear-gradient(90deg,#ff7a7a,#ff5252)' : 'linear-gradient(90deg,#8ef0c2,#10b981)');

  const title = document.createElement('div'); title.className = 'title'; title.textContent = (type === 'error' ? 'Error' : 'Success');
  const msg = document.createElement('div'); msg.className = 'msg'; msg.textContent = message;
  const progress = document.createElement('div'); progress.className = 'progress';
  const bar = document.createElement('i'); progress.appendChild(bar);

  toast.appendChild(title); toast.appendChild(msg); toast.appendChild(progress);
  wrap.appendChild(toast);

  // remove after duration + small buffer
  setTimeout(()=>{
    toast.style.transition = 'opacity .25s, transform .25s';
    toast.style.opacity = '0'; toast.style.transform = 'translateY(-10px)';
    setTimeout(()=>wrap.removeChild(toast),300);
  }, duration);
}

document.addEventListener('DOMContentLoaded', function(){
  try{
    if(window.FLASK_MESSAGES && Array.isArray(window.FLASK_MESSAGES)){
      window.FLASK_MESSAGES.forEach(function(item){
        // item is [category, message] or [category, message]? Flask returns (category, message) when with_categories=True
        if(Array.isArray(item) && item.length >= 2){
          const category = item[0] || 'message';
          const msg = item[1] || '';
          makeToast(msg, category === 'error' ? 'error' : 'success', 4500);
        } else if(typeof item === 'string'){
          makeToast(item, 'success', 4500);
        }
      });
    }
  }catch(e){ console.error('notify error', e); }
});
