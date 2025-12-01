// Toast 管理器 - 简单直接的客户端实现
window.toastManager = {
    show(message, category = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) {
            console.error('Toast container not found');
            return;
        }
        
        // 创建 toast 元素
        const toastDiv = document.createElement('div');
        toastDiv.className = `toast max-w-md w-full shadow-lg rounded-lg pointer-events-auto overflow-hidden mb-2 ${
            category === 'success' ? 'bg-green-500' :
            category === 'error' ? 'bg-red-500' :
            category === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
        }`;
        
        // 图标 SVG
        const icons = {
            success: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />',
            error: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />',
            warning: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />',
            info: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />'
        };
        
        toastDiv.innerHTML = `
            <div class="p-4">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            ${icons[category] || icons.info}
                        </svg>
                    </div>
                    <div class="ml-3 flex-1">
                        <p class="text-sm font-medium text-white">${message}</p>
                    </div>
                    <div class="ml-4 flex-shrink-0 flex">
                        <button class="inline-flex text-white hover:text-gray-200 focus:outline-none" onclick="this.closest('.toast').remove()">
                            <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // 添加到容器
        container.appendChild(toastDiv);
        
        // 添加进入动画
        toastDiv.style.opacity = '0';
        toastDiv.style.transform = 'translateX(100%)';
        toastDiv.style.transition = 'all 0.3s ease-out';
        
        // 触发动画
        setTimeout(() => {
            toastDiv.style.opacity = '1';
            toastDiv.style.transform = 'translateX(0)';
        }, 10);
        
        // 5秒后自动移除
        setTimeout(() => {
            toastDiv.style.opacity = '0';
            toastDiv.style.transform = 'translateX(100%)';
            setTimeout(() => toastDiv.remove(), 300);
        }, 5000);
    }
};

// 初始化页面加载时的 toast
document.addEventListener('DOMContentLoaded', () => {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        // 触发进入动画
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }, 10);
        
        // 5秒后自动移除
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    });
});

// 全局错误处理
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// 防止表单重复提交
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.classList.contains('submitting')) {
        e.preventDefault();
        return false;
    }
    form.classList.add('submitting');
    setTimeout(() => form.classList.remove('submitting'), 3000);
});

// 查看快照
async function viewSnapshot(snapshotId) {
    const response = await fetch(`/api/snapshots/${snapshotId}`);
    if (response.ok) {
        const snapshot = await response.json();
        const win = window.open('', '_blank');
        win.document.write(`<pre>${snapshot.yaml}</pre>`);
    }
}
