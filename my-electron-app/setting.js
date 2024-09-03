function loadPage(){
    window.location.href = 'index.html';
}

window.electronAPI.receiveRelicsData((relics) => {
    const container = document.getElementById('yiqi');
    relics.filter(relic => relic.type === '外圈').forEach(relic => {
      const relicDiv = document.createElement('div');
      relicDiv.classList.add('relic');
      relicDiv.innerHTML = `
        <h2>${relic.name}</h2>
        <img src="${relic.tagImageUrl}" alt="Tag Image" />
        <p>类型: ${relic.type}</p>
        <div>
          <h3>详情</h3>
          <p>头部: ${relic.details.head ? `<img src="${relic.details.head}" alt="Head Image" />` : '无'}</p>
          <p>手部: ${relic.details.hands ? `<img src="${relic.details.hands}" alt="Hands Image" />` : '无'}</p>
          <p>躯干: ${relic.details.body ? `<img src="${relic.details.body}" alt="Body Image" />` : '无'}</p>
          <p>脚部: ${relic.details.feet ? `<img src="${relic.details.feet}" alt="Feet Image" />` : '无'}</p>
        </div>
      `;
      container.appendChild(relicDiv);
    });
    relics.filter(relic => relic.type === '内圈').forEach(relic => {
        const relicDiv = document.createElement('div');
        relicDiv.classList.add('relic');
        relicDiv.innerHTML = `
          <h2>${relic.name}</h2>
          <img src="${relic.tagImageUrl}" alt="Tag Image" />
          <p>类型: ${relic.type}</p>
          <div>
            <h3>详情</h3>
            <p>头部: ${relic.details.sphere ? `<img src="${relic.details.sphere}" alt="Head Image" />` : '无'}</p>
            <p>手部: ${relic.details.rope ? `<img src="${relic.details.rope}" alt="Hands Image" />` : '无'}</p>
            
          </div>
        `;
        container.appendChild(relicDiv);
      });
  });
