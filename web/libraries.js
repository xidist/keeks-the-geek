"use strict";
const search=document.getElementById('tool-search');
search.addEventListener('input',()=>{const q=search.value.toLowerCase().trim();let count=0;
document.querySelectorAll('.tool-card').forEach(card=>{card.hidden=!card.dataset.search.includes(q);if(!card.hidden)count++;});
document.querySelectorAll('.tool-group').forEach(group=>group.hidden=![...group.querySelectorAll('.tool-card')].some(card=>!card.hidden));
document.getElementById('result-count').textContent=count+' of 101 tools';document.getElementById('no-results').hidden=count!==0;});
