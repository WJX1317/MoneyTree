async function renderTree(goalId) {
    const res = await fetch(`/api/tree/${goalId}`);
    const data = await res.json();
    const container = document.getElementById('tree-container');
    container.innerHTML = '';

    data.nodes.forEach(node => {
        const div = document.createElement('div');
        div.className = `tree-node ${node.status}`;
        div.dataset.nodeId = node.id;
        const statusIcons = {locked: '🔒', unlocked: '📖', learned: '⏳', verified: '✅'};
        div.textContent = `${statusIcons[node.status] || ''} ${node.title}`;
        div.addEventListener('click', () => {
            if (node.status !== 'locked') {
                switchToNode(node);
            }
        });
        container.appendChild(div);
    });
}

function highlightNode(nodeId) {
    document.querySelectorAll('.tree-node').forEach(n => n.classList.remove('active'));
    const el = document.querySelector(`[data-node-id="${nodeId}"]`);
    if (el) el.classList.add('active');
}
