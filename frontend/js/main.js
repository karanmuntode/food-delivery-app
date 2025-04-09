document.addEventListener("DOMContentLoaded", () => {
  // ====================== REGISTER ======================
  const registerForm = document.getElementById("registerForm");

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("name").value.trim();
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value.trim();
      const role = document.getElementById("role")?.value || "customer";

      try {
        const response = await fetch("http://localhost:8000/api/register/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, email, password, role }),
        });

        const result = await response.json();

        if (response.ok) {
          alert("Registration successful! Please login.");
          window.location.href = "login.html";
        } else {
          alert(result.error || result.detail || "Registration failed.");
        }
      } catch (err) {
        console.error("Registration error:", err);
        alert("Something went wrong. Please try again.");
      }
    });
  }

  // ====================== LOGIN ======================
  const loginForm = document.getElementById("loginForm");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value.trim();

      try {
        const response = await fetch("http://localhost:8000/api/token/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: email, password }),
        });

        const result = await response.json();

        if (response.ok) {
          localStorage.setItem("access", result.access);
          localStorage.setItem("refresh", result.refresh);
          localStorage.setItem("email", email);
          localStorage.setItem("role", result.role);

          const dashRes = await fetch("http://localhost:8000/api/dashboard/", {
            headers: {
              Authorization: `Bearer ${result.access}`,
            },
          });

          const dashboard = await dashRes.json();
          console.log("Dashboard:", dashboard);

          if (dashboard.role === "restaurant") {
            if (dashboard.restaurant) {
              window.location.href = "owner_dashboard.html";
            } else {
              window.location.href = "restaurant_register.html";
            }
          } else if (dashboard.role === "customer") {
            window.location.href = "dashboard.html";
          } else {
            alert("Unsupported role. Contact admin.");
          }
        } else {
          alert(result.detail || "Invalid email or password.");
        }
      } catch (error) {
        console.error("Login error:", error);
        alert("Server error. Please try again later.");
      }
    });
  }

  // ====================== LOAD RESTAURANTS (Homepage) ======================
  const container = document.getElementById("featured-restaurants");

  if (container) {
    const token = localStorage.getItem("access");

    fetch("http://localhost:8000/api/restaurants/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => {
        if (!response.ok) throw new Error("Unauthorized");
        return response.json();
      })
      .then((data) => {
        container.innerHTML = "";
        data.forEach((restaurant) => {
          container.innerHTML += `
            <div class="col-md-4 mb-4">
              <div class="card shadow">
                <img src="${restaurant.image || 'https://source.unsplash.com/400x250/?restaurant,food'}" class="card-img-top" alt="${restaurant.name}">
                <div class="card-body">
                  <h5 class="card-title">${restaurant.name}</h5>
                  <p class="card-text">${restaurant.description}</p>
                  <a href="restaurant.html?id=${restaurant.id}" class="btn btn-outline-danger">View Menu</a>
                </div>
              </div>
            </div>
          `;
        });
      })
      .catch((error) => {
        console.error("Failed to load restaurants:", error);
        container.innerHTML = `<p class="text-center text-danger">Please login to view restaurants.</p>`;
      });
  }
});
