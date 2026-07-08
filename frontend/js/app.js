const state = {
    currentGoalId: null,
    currentNodeId: null,
    currentPhase: null,
};

function switchView(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById(`view-${viewName}`).classList.add('active');
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');

    if (viewName === 'journal') loadJournal();
    if (viewName === 'passport') loadPassport();
}

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        switchView(item.dataset.view);
    });
});

document.getElementById('new-goal-btn').addEventListener('click', () => {
    document.getElementById('goal-modal').style.display = 'flex';
    document.getElementById('goal-input').focus();
});

document.getElementById('goal-cancel').addEventListener('click', () => {
    document.getElementById('goal-modal').style.display = 'none';
});

document.getElementById('goal-submit').addEventListener('click', async () => {
    const title = document.getElementById('goal-input').value.trim();
    if (!title) return;

    document.getElementById('goal-modal').style.display = 'none';
    document.getElementById('goal-input').value = '';

    const info = document.getElementById('current-node-info');
    info.style.display = 'block';
    info.textContent = `正在为「${title}」规划知识树，请稍候...`;
    disableChat();
    clearChat();
    document.getElementById('tree-container').innerHTML = '<div style="color:#94a3b8;font-size:0.8rem;padding:8px;">生成中...</div>';

    try {
        const res = await fetch('/api/goals', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title}),
        });
        if (!res.ok) {
            const info = document.getElementById('current-node-info');
            info.textContent = '创建失败，请重试';
            return;
        }
        const data = await res.json();
        await loadGoals();
        selectGoal(data.goal_id);
    } catch (e) {
        const info = document.getElementById('current-node-info');
        info.textContent = '创建失败：' + e.message;
    }
});

async function loadGoals() {
    const res = await fetch('/api/goals');
    const goals = await res.json();
    const sel = document.getElementById('goal-select');
    sel.innerHTML = '<option value="">-- 选择学习目标 --</option>';
    goals.forEach(g => {
        const opt = document.createElement('option');
        opt.value = g.id;
        opt.textContent = g.title;
        sel.appendChild(opt);
    });
}

document.getElementById('goal-select').addEventListener('change', (e) => {
    if (e.target.value) selectGoal(e.target.value);
});

async function selectGoal(goalId) {
    state.currentGoalId = goalId;
    document.getElementById('goal-select').value = goalId;
    await renderTree(goalId);
    await loadCurrentNode(goalId);
}

async function loadCurrentNode(goalId) {
    const res = await fetch(`/api/tree/${goalId}/current`);
    const data = await res.json();
    const info = document.getElementById('current-node-info');

    if (data.all_done) {
        info.style.display = 'block';
        info.textContent = '恭喜！所有知识点已学完并通过验证！';
        disableChat();
        return;
    }

    const node = data.node;
    switchToNode(node);
}

async function switchToNode(node) {
    state.currentNodeId = node.id;
    state.currentPhase = node.status === 'learned' ? 'verify' : 'teach';

    const info = document.getElementById('current-node-info');
    info.style.display = 'block';
    info.textContent = state.currentPhase === 'teach'
        ? `当前学习：${node.title}`
        : `验证理解：${node.title}`;

    enableChat();
    clearChat();
    highlightNode(node.id);
    await loadChatHistory(node.id);
}

async function loadChatHistory(nodeId) {
    const res = await fetch(`/api/chat/history/${nodeId}`);
    const data = await res.json();
    if (data.history && data.history.length > 0) {
        const phase = state.currentPhase;
        const filtered = data.history.filter(msg => msg.phase === phase);
        if (filtered.length > 0) {
            filtered.forEach(msg => {
                appendMessage(msg.role, msg.content);
            });
        } else {
            await sendMessage('');
        }
    } else {
        await sendMessage('');
    }
}

function disableChat() {
    document.getElementById('chat-input').disabled = true;
    document.getElementById('chat-send').disabled = true;
}

function enableChat() {
    document.getElementById('chat-input').disabled = false;
    document.getElementById('chat-send').disabled = false;
}

loadGoals();
