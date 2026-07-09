const md = window.markdownit({ html: false, linkify: true, breaks: true });

mermaid.initialize({ startOnLoad: false, theme: 'neutral' });

function renderMarkdown(text) {
    let html = md.render(text);
    html = html.replace(/<pre><code class="language-mermaid">([\s\S]*?)<\/code><\/pre>/g, (match, code) => {
        const decoded = code.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"');
        return `<div class="mermaid">${decoded}</div>`;
    });
    return html;
}

function showVerifyTransition(nodeTitle) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.id = 'transition-msg';
    div.innerHTML = `<div class="bubble transition-buttons">
        <button class="btn-continue" onclick="continueTeaching()">我还有问题</button>
        <button class="btn-verify" onclick="startVerify('${nodeTitle.replace(/'/g, "\\'")}')">开始验证</button>
    </div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    disableChat();
}

function continueTeaching() {
    document.getElementById('transition-msg')?.remove();
    state.currentPhase = 'teach';
    enableChat();
    document.getElementById('chat-input').focus();
}

function startVerify(nodeTitle) {
    document.getElementById('transition-msg')?.remove();
    state.currentPhase = 'verify';
    const info = document.getElementById('current-node-info');
    info.textContent = `验证理解：${nodeTitle}`;
    enableChat();
    sendMessage('');
}

function clearChat() {
    document.getElementById('chat-messages').innerHTML = '';
    removeQuickOptions();
}

function showQuickOptions(options) {
    removeQuickOptions();
    const area = document.querySelector('.chat-input-area');
    const container = document.createElement('div');
    container.className = 'quick-options';
    container.id = 'quick-options';
    options.forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'quick-opt-btn';
        btn.textContent = opt;
        btn.addEventListener('click', () => {
            removeQuickOptions();
            document.getElementById('chat-input').value = '';
            sendMessage(opt);
        });
        container.appendChild(btn);
    });
    area.parentNode.insertBefore(container, area);
}

function removeQuickOptions() {
    const el = document.getElementById('quick-options');
    if (el) el.remove();
}

function appendMessage(role, text, time) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `message ${role}`;
    const timeHtml = time ? `<div class="msg-time">${formatTime(time)}</div>` : '';
    if (role === 'assistant') {
        div.innerHTML = `<div class="bubble">${renderMarkdown(text)}</div>${timeHtml}`;
    } else {
        div.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>${timeHtml}`;
    }
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    mermaid.run({ nodes: div.querySelectorAll('.mermaid') });
}

function formatTime(timeStr) {
    if (!timeStr) return '';
    const d = new Date(timeStr);
    if (isNaN(d.getTime())) return '';
    const month = d.getMonth() + 1;
    const day = d.getDate();
    const h = String(d.getHours()).padStart(2, '0');
    const m = String(d.getMinutes()).padStart(2, '0');
    return `${month}/${day} ${h}:${m}`;
}

async function undoLastMessage() {
    if (abortController) {
        abortController.abort();
        removeLoading();
        isSending = false;
        abortController = null;
        document.getElementById('chat-send').disabled = false;
        document.getElementById('chat-input').disabled = false;
    }

    const container = document.getElementById('chat-messages');
    const messages = container.querySelectorAll('.message');
    if (messages.length === 0) return;

    const lastMsg = messages[messages.length - 1];
    let undoneText = '';

    if (lastMsg.classList.contains('assistant') && messages.length >= 2) {
        const secondLast = messages[messages.length - 2];
        if (secondLast.classList.contains('user')) {
            undoneText = secondLast.querySelector('.bubble').textContent;
            try {
                await fetch(`/api/chat/undo/${state.currentNodeId}`, { method: 'POST' });
                lastMsg.remove();
                secondLast.remove();
            } catch (e) { return; }
        }
    } else if (lastMsg.classList.contains('user')) {
        undoneText = lastMsg.querySelector('.bubble').textContent;
        try {
            await fetch(`/api/chat/undo-last/${state.currentNodeId}`, { method: 'POST' });
            lastMsg.remove();
        } catch (e) { return; }
    }

    if (undoneText) {
        const input = document.getElementById('chat-input');
        input.value = undoneText;
        input.focus();
    }
}

function appendLoading() {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.id = 'loading-msg';
    div.innerHTML = '<div class="bubble">正在思考...</div>';
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function removeLoading() {
    const el = document.getElementById('loading-msg');
    if (el) el.remove();
}

function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

let isSending = false;
let abortController = null;

async function sendMessage(userText) {
    if (isSending) return;
    isSending = true;
    abortController = new AbortController();

    if (userText) {
        appendMessage('user', userText);
    }

    removeQuickOptions();
    document.getElementById('chat-input').value = '';
    document.getElementById('chat-send').disabled = true;
    document.getElementById('chat-input').disabled = true;
    appendLoading();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                goal_id: state.currentGoalId,
                node_id: state.currentNodeId,
                message: userText || '',
                phase: state.currentPhase || '',
            }),
            signal: abortController.signal,
        });

        removeLoading();

        if (!res.ok) {
            appendMessage('assistant', '请求失败，请重试。');
            return;
        }

        const data = await res.json();

        if (data.error) {
            appendMessage('assistant', '错误：' + data.error);
            return;
        }

        appendMessage('assistant', data.reply);

        if (data.options && data.options.length > 0) {
            showQuickOptions(data.options);
        }

        if (data.teaching_complete) {
            await renderTree(state.currentGoalId);
            const nodes = await (await fetch(`/api/tree/${state.currentGoalId}`)).json();
            const node = nodes.nodes.find(n => n.id === state.currentNodeId);
            appendMessage('assistant', '这个知识点讲完啦！如果还有疑问可以继续问，准备好了就点"开始验证"。');
            showVerifyTransition(node ? node.title : '');
            return;
        }

        if (data.verified) {
            appendMessage('assistant', '恭喜通过验证！进入下一个知识点...');
            await renderTree(state.currentGoalId);
            setTimeout(async () => {
                clearChat();
                await loadCurrentNode(state.currentGoalId);
            }, 1000);
            return;
        }
    } catch (e) {
        removeLoading();
        if (e.name === 'AbortError') return;
        appendMessage('assistant', '网络错误：' + e.message);
    } finally {
        isSending = false;
        abortController = null;
        document.getElementById('chat-send').disabled = false;
        document.getElementById('chat-input').disabled = false;
        document.getElementById('chat-undo').disabled = false;
        document.getElementById('chat-input').focus();
    }
}

document.getElementById('chat-send').addEventListener('click', () => {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (text && !isSending) {
        input.value = '';
        sendMessage(text);
    }
});

document.getElementById('chat-undo').addEventListener('click', () => {
    undoLastMessage();
});

document.getElementById('chat-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('chat-send').click();
    }
});
