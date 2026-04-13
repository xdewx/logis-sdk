document.addEventListener( 'DOMContentLoaded', function () {
  // FIXME: 发现还不如默认情况
  return
  // 找到所有已展开的导航菜单，强制关闭
  const expandedItems = document.querySelectorAll('.md-nav__item--active > .md-nav__link--active + .md-nav');
  expandedItems.forEach(item => {
    item.style.display = 'none';
    // 重置展开状态标记
    const parent = item.closest('.md-nav__item');
    parent.classList.remove('md-nav__item--expanded');
  });
});