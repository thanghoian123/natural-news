<template>
    <div class="layout">
      <!-- Left Sidebar (Navigation) -->
      <aside class="sidebar">
        <img alt="logo" class="logo" src="@/assets/hrs-logo.png" />
        <nav>
            <router-link to="/video-report" class="nav-btn">Animated video book reports</router-link>
          <router-link to="/chat" class="nav-btn">Chat with Enoch</router-link>
          <router-link to="/ingredient-checker" class="nav-btn">Ingredient Checker</router-link>
        </nav>
      </aside>
  
      <!-- Right Content Area -->
      <main class="content">
        <router-view></router-view>
      </main>
    </div>
</template>
  
<style scoped>
.layout {
    width: 100vw;
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 200px;
  background: #f47f20;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center; /* Center logo and nav items */
}

.logo {
  width: 100px; /* Adjust logo size */
  height: auto;
  margin-bottom: 20px; /* Add spacing below logo */
}

.nav-btn {
  display: block;
  padding: 10px;
  margin-bottom: 10px;
  color: white;
  text-decoration: none;
  background: #34495e;
  text-align: center;
  border-radius: 5px;
  width: 100%; /* Make buttons full width */
}

.nav-btn:hover {
  background: #1abc9c;
}

.content {
  flex: 1; /* Makes content take remaining space */
  padding: 20px;
  overflow: auto; /* Ensures content doesn't break the layout */
}
</style>
