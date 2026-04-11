<template>
  <section class="card auth-card">
    <h2>Acceso restringido</h2>
    <p>Esta seccion requiere rol de administrador.</p>
    <RouterLink class="link-btn" to="/login">Volver a login</RouterLink>
  </section>
</template>

<style scoped>
.auth-card {
  max-width: 520px;
  margin: 0 auto;
}
</style>
