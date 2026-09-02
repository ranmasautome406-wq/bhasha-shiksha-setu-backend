let API_BASE = localStorage.getItem("bhasha_api_url") || "";

let requests = 0;
let events = [];

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);


/* =========================
   TOAST
========================= */

function toast(message) {

    const element = $("#toast");

    element.textContent = message;

    element.classList.add("show");

    clearTimeout(window.toastTimer);

    window.toastTimer = setTimeout(() => {
        element.classList.remove("show");
    }, 2500);
}


/* =========================
   ACTIVITY LOG
========================= */

function logActivity(message) {

    events.unshift({
        message: message,
        time: new Date().toLocaleTimeString()
    });

    renderActivity();
}


function renderActivity() {

    const html = events.map(event => {

        return `
            <div class="activity">

                <span class="status-dot"></span>

                <div>
                    <b>${escapeHTML(event.message)}</b>
                    <small>${escapeHTML(event.time)}</small>
                </div>

            </div>
        `;

    }).join("");

    $("#activityList").innerHTML =
        html || "<p>No activity yet.</p>";

    $("#fullActivity").innerHTML =
        html || "<p>No activity yet.</p>";

    $("#requests").textContent = requests;
}


function escapeHTML(value) {

    return String(value).replace(
        /[&<>"']/g,
        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[character]
    );
}


/* =========================
   PAGE NAVIGATION
========================= */

function showPage(pageId) {

    $$(".page").forEach(page => {
        page.classList.remove("active");
    });

    const selectedPage = $("#" + pageId);

    if (selectedPage) {
        selectedPage.classList.add("active");
    }

    $$(".nav-item").forEach(item => {

        item.classList.toggle(
            "active",
            item.dataset.section === pageId
        );

    });

    const titles = {

        dashboard: "Dashboard",
        students: "Students",
        teachers: "Teachers",
        lessons: "Lessons",
        tutor: "AI Tutor",
        languages: "Languages",
        uploads: "Uploads",
        activity: "Activity",
        settings: "Settings"

    };

    $("#pageTitle").textContent =
        titles[pageId] || "Dashboard";

    $("#sidebar").classList.remove("open");
}


/* Sidebar navigation */

$$(".nav-item").forEach(item => {

    item.addEventListener("click", () => {

        showPage(item.dataset.section);

    });

});


/* Quick actions */

$$(".quick-actions button").forEach(button => {

    button.addEventListener("click", () => {

        showPage(button.dataset.section);

    });

});


/* Mobile menu */

$("#menuBtn").addEventListener("click", () => {

    $("#sidebar").classList.toggle("open");

});


/* Clear activity */

$("#clearActivity").addEventListener("click", () => {

    events = [];

    renderActivity();

    toast("Activity cleared");

});


/* =========================
   API HEALTH
========================= */

async function checkAPIHealth() {

    if (!API_BASE) {

        $("#apiStatus").textContent = "Not Set";

        $("#apiMessage").textContent =
            "Add backend URL in Settings";

        $("#systemStatus").textContent =
            "Backend URL missing";

        return;
    }

    requests++;

    $("#apiStatus").textContent = "Checking";

    $("#apiMessage").textContent =
        "Connecting to backend...";

    try {

        const response = await fetch(
            API_BASE.replace(/\/$/, "") + "/api/health"
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                "HTTP " + response.status
            );
        }

        $("#apiStatus").textContent = "Online";

        $("#apiMessage").textContent =
            data.message || "Backend is healthy";

        $("#systemStatus").textContent =
            "API connected";

        toast("Backend API is online ✓");

        logActivity(
            "API health check succeeded"
        );

    } catch (error) {

        $("#apiStatus").textContent =
            "Offline";

        $("#apiMessage").textContent =
            error.message;

        $("#systemStatus").textContent =
            "API unavailable";

        toast("Backend connection failed");

        logActivity(
            "API health check failed"
        );
    }

    renderActivity();
}


/* API buttons */

$("#healthBtn").addEventListener(
    "click",
    checkAPIHealth
);

$("#refreshBtn").addEventListener(
    "click",
    checkAPIHealth
);


/* =========================
   FILE UPLOAD UI
========================= */

$("#chooseFiles").addEventListener(
    "click",
    () => $("#fileInput").click()
);


$("#fileInput").addEventListener(
    "change",
    () => {

        const files =
            Array.from($("#fileInput").files);

        if (!files.length) {
            return;
        }

        $("#fileNames").textContent =
            files.map(file => file.name).join(", ");

        toast(
            files.length +
            " file(s) selected"
        );

        logActivity(
            files.length +
            " file(s) selected for upload"
        );
    }
);


/* =========================
   SETTINGS
========================= */

$("#apiUrl").value = API_BASE;


$("#saveApi").addEventListener(
    "click",
    () => {

        const url =
            $("#apiUrl").value.trim().replace(/\/$/, "");

        if (!url) {

            toast(
                "Please enter your backend URL"
            );

            return;
        }

        localStorage.setItem(
            "bhasha_api_url",
            url
        );

        API_BASE = url;

        toast(
            "Backend URL saved successfully"
        );

        logActivity(
            "Backend API URL updated"
        );

        checkAPIHealth();
    }
);


/* =========================
   INITIALIZATION
========================= */

logActivity(
    "Admin dashboard initialized"
);

renderActivity();

checkAPIHealth();
