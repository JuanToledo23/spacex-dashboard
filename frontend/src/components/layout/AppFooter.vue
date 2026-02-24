<template>
  <footer class="footer">
    <span class="footer-left">SpaceX · Juan Alberto Toledo Tello</span>
    <span class="footer-right">Data from api.spacexdata.com</span>
  </footer>
</template>

<style scoped>
.footer {
  border-top: 1px solid var(--border);
  margin-top: auto;
  max-width: 1200px;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding: 14px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  opacity: 0.5;
}

.footer-right {
  opacity: 0.6;
}

@media (max-width: 640px) {
  .footer { padding: 12px 16px; }
  .footer-right { display: none; }
}
</style>
