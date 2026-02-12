
document.addEventListener('DOMContentLoaded', ()=>{
  const sideBar = document.querySelector('.side-bar');
  const menuBtn = document.getElementById('menu-btn');
  const closeBtn = document.getElementById('close-btn');
  const userBtn = document.getElementById('user-btn');
  const headerProfile = document.querySelector('.header .profile');

  if(menuBtn && sideBar){
    menuBtn.addEventListener('click', ()=> sideBar.classList.add('active'));
  }
  if(closeBtn && sideBar){
    closeBtn.addEventListener('click', ()=> sideBar.classList.remove('active'));
  }
  if(userBtn && headerProfile){
    userBtn.addEventListener('click', ()=> headerProfile.classList.toggle('active'));
  }
});
