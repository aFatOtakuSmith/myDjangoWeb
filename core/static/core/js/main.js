document.addEventListener("DOMContentLoaded", function() {
    
    // ==========================================
    // 1. 水波涟漪点击特效
    // ==========================================
    document.addEventListener('click', function(e) {
        const ripple = document.createElement('div');
        ripple.classList.add('click-ripple');
        
        ripple.style.width = '30px';
        ripple.style.height = '30px';
        ripple.style.left = e.clientX + 'px';
        ripple.style.top = e.clientY + 'px';
        
        document.body.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 500);
    });


    // ==========================================
    // 2. 左侧悬挂装饰物 (上下浮动 + 左右摆动)
    // ==========================================
    const wrapper = document.getElementById('hangingWrapper');
    const item = document.getElementById('hangingItem');

    function updateHangingPosition() {
        if (!wrapper || !item) return; 

        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        
        if (docHeight <= 0) return;

        const progress = scrollTop / docHeight;
        const trackHeight = wrapper.offsetHeight - item.offsetHeight;
        const topPosition = progress * trackHeight;
        const swayX = Math.sin(progress * Math.PI * 2) * 12;
        const rotateAngle = (swayX / 12) * 8; 

        item.style.top = `${topPosition}px`;
        item.style.transform = `translateX(calc(-50% + ${swayX}px)) rotate(${rotateAngle}deg)`;
    }

    window.addEventListener('scroll', updateHangingPosition);
    window.addEventListener('resize', updateHangingPosition);
    updateHangingPosition();


    // ==========================================
    // 3. 卡片 3D 倾斜特效
    // ==========================================
    const cards = document.querySelectorAll('.glass-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left; 
            const y = e.clientY - rect.top;  
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = ((y - centerY) / centerY) * -10; 
            const rotateY = ((x - centerX) / centerX) * 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
            // 🌟 修改：把 0.3 改成了 0.15，让 3D 倾斜时的发光阴影变得柔和
            card.style.boxShadow = `${-rotateY}px ${rotateX}px 30px rgba(14, 165, 233, 0.15)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = `perspective(1000px) rotateX(0) rotateY(0) scale(1)`;
            // 🌟 修改：恢复时的阴影也变淡
            card.style.boxShadow = `0 8px 24px rgba(14, 165, 233, 0.08)`;
        });
    });

});