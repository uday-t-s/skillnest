
// Basic front-end logic for SkillNest demo project

window.SkillNest = (function(){
  const CAREER_SKILLS = {
    frontend: ['html','css','javascript','react','git','responsive design'],
    backend: ['javascript','node.js','express','sql','apis','git'],
    data_scientist: ['python','statistics','pandas','numpy','sql','machine learning'],
    ui_ux: ['figma','wireframing','prototyping','user research','visual design'],
    devops: ['linux','docker','ci/cd','git','cloud','kubernetes'],
    ai_engineer: ['python','deep learning','pytorch','tensorflow','mlops'],
    mobile_dev: ['java','kotlin','android','swift','ios','git'],
    cybersec: ['networking','linux','security','owasp','siem'],
    cloud_architect: ['aws','azure','gcp','networking','security','terraform']
  };

  function normalizeSkill(s){
    return s.trim().toLowerCase();
  }

  function skillGap(careerKey, userSkillsRaw){
    const universe = CAREER_SKILLS[careerKey] || [];
    const userSet = new Set(userSkillsRaw.map(normalizeSkill));
    const have = [];
    const missing = [];
    universe.forEach(s=>{
      if(userSet.has(s.toLowerCase())) have.push(s);
      else missing.push(s);
    });
    return {have, missing};
  }

  function suggestCareers(userSkillsRaw){
    const userSet = new Set(userSkillsRaw.map(normalizeSkill));
    const results = [];
    Object.entries(CAREER_SKILLS).forEach(([careerId, needed])=>{
      let matched = 0;
      needed.forEach(s=>{
        if(userSet.has(s.toLowerCase())) matched++;
      });
      const score = needed.length ? matched / needed.length : 0;
      const missingSkills = needed.filter(s=>!userSet.has(s.toLowerCase()));
      const title = careerId.replace(/_/g,' ').replace(/\b\w/g, c=>c.toUpperCase());
      results.push({careerId, title, score, missingSkills});
    });
    results.sort((a,b)=>b.score - a.score);
    return results;
  }

  return {CAREER_SKILLS, skillGap, suggestCareers};
})();

// Simple mock jobs for placement page
function SkillNestRenderJobs(){
  const jobsEl = document.getElementById('jobs');
  if(!jobsEl) return;
  const jobs = [
    {
      title: 'Associate Frontend Developer',
      company: 'AlphaTech',
      location: 'Bengaluru · Remote',
      match: 88,
      skills: ['React','JavaScript','HTML/CSS','Git'],
      ctc: '5–7 LPA'
    },
    {
      title: 'Junior Data Analyst',
      company: 'DataPlus',
      location: 'Pune · Hybrid',
      match: 72,
      skills: ['SQL','Excel','Python','Power BI'],
      ctc: '4–6 LPA'
    },
    {
      title: 'Backend Developer (Node.js)',
      company: 'CloudBridge',
      location: 'Remote',
      match: 65,
      skills: ['Node.js','Express','MongoDB','APIs'],
      ctc: '6–8 LPA'
    }
  ];

  jobsEl.innerHTML = jobs.map(j=>`
    <article class="box">
      <h3>${j.title}</h3>
      <p><strong>${j.company}</strong> · ${j.location}</p>
      <p><strong>Skills:</strong> ${j.skills.join(', ')}</p>
     <p><strong>CTC:</strong> ${j.ctc}</p>
<p style="margin-top:4px;">Estimated Match: <strong>${j.match}%</strong></p>

<a href="apply.html?job=${encodeURIComponent(j.title)}&company=${encodeURIComponent(j.company)}"
   class="inline-btn" style="margin-top:8px; display:inline-block;">
   Apply Now
</a>

    </article>
  `).join('');
}

document.addEventListener('DOMContentLoaded', SkillNestRenderJobs);


// Simple portfolio management using localStorage
(function(){
  const KEY = 'skillnest_portfolio_projects';

  function loadProjects(){
    try {
      const raw = localStorage.getItem(KEY);
      if(!raw) return [];
      return JSON.parse(raw);
    } catch(e){
      return [];
    }
  }

  function saveProjects(list){
    localStorage.setItem(KEY, JSON.stringify(list));
  }

  window.SkillNest.getPortfolio = function(){
    return loadProjects();
  };

  window.SkillNest.addProject = function(project){
    const list = loadProjects();
    list.push(project);
    saveProjects(list);
  };

  window.SkillNest.deleteProject = function(idx){
    const list = loadProjects();
    list.splice(idx,1);
    saveProjects(list);
  };
})();
