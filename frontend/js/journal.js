async function loadJournal() {
    const res = await fetch('/api/journal');
    const entries = await res.json();
    const list = document.getElementById('journal-list');
    if (entries.length === 0) {
        list.innerHTML = '<p style="color:#94a3b8;">还没有投资记录。点击右上角添加第一条。</p>';
        return;
    }
    list.innerHTML = entries.map(e => `
        <div class="journal-entry">
            <strong>${e.action} ${e.asset}</strong>
            ${e.amount ? ` · ${e.amount}` : ''}${e.cost ? ` · 成本${e.cost}` : ''}
            <div class="meta">${e.date}${e.reason ? ' · ' + e.reason : ''}</div>
        </div>
    `).join('');
}

document.getElementById('new-journal-btn').addEventListener('click', () => {
    document.getElementById('journal-modal').style.display = 'flex';
    document.querySelector('#journal-form [name="date"]').valueAsDate = new Date();
});

document.getElementById('cancel-journal').addEventListener('click', () => {
    document.getElementById('journal-modal').style.display = 'none';
});

document.getElementById('journal-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const body = {
        date: form.date.value,
        action: form.action.value,
        asset: form.asset.value,
        amount: form.amount.value,
        cost: form.cost.value,
        reason: form.reason.value,
    };
    await fetch('/api/journal', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body),
    });
    document.getElementById('journal-modal').style.display = 'none';
    form.reset();
    loadJournal();
});

async function loadPassport() {
    const res = await fetch('/api/passport');
    const data = await res.json();
    const container = document.getElementById('passport-content');
    if (data.goals.length === 0) {
        container.innerHTML = '<p style="color:#94a3b8;">还没有学习目标。去"学习"页面创建一个吧。</p>';
        return;
    }
    container.innerHTML = data.goals.map(g => `
        <div class="passport-goal" onclick="goToGoal('${g.id}')" style="cursor:pointer;">
            <h3>${g.title}</h3>
            <p>已验证 ${g.verified_nodes} / ${g.total_nodes} 个知识点</p>
            <div class="progress-bar">
                <div class="fill" style="width:${g.progress}%"></div>
            </div>
            <div class="passport-nodes" id="passport-nodes-${g.id}"></div>
        </div>
    `).join('');
    for (const g of data.goals) {
        const nodesRes = await fetch(`/api/tree/${g.id}`);
        const nodesData = await nodesRes.json();
        const nodesEl = document.getElementById(`passport-nodes-${g.id}`);
        if (nodesData.nodes) {
            nodesEl.innerHTML = nodesData.nodes.map(n => {
                const icon = n.status === 'verified' ? '✅' : n.status === 'learned' ? '⏳' : n.status === 'unlocked' ? '📖' : '🔒';
                return `<span class="passport-node-badge ${n.status}">${icon} ${n.title}</span>`;
            }).join('');
        }
    }
}

function goToGoal(goalId) {
    switchView('learn');
    selectGoal(goalId);
}
