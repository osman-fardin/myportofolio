const projectIndex = document.getElementById('project-index');

function createProjectLink(project, index) {
    const link = document.createElement('a');
    const number = document.createElement('span');
    const textWrapper = document.createElement('span');
    const title = document.createElement('span');
    const type = document.createElement('span');

    link.className = 'project-index-item';
    link.href = project.detail_url;

    if (window.location.pathname === project.detail_url) {
        link.classList.add('is-selected');
        link.setAttribute('aria-current', 'page');
    }

    number.className = 'project-number';
    number.textContent = String(index + 1).padStart(2, '0');

    title.className = 'project-index-title';
    title.textContent = project.fields.title;

    type.className = 'project-index-type';
    type.textContent = project.fields.project_type;

    textWrapper.append(title, type);
    link.append(number, textWrapper);

    return link;
}

async function loadProjects() {
    const endpoint = new URL(
        projectIndex.dataset.projectsUrl,
        window.location.origin,
    );

    endpoint.search = window.location.search;

    const response = await fetch(endpoint);

    if (!response.ok) {
        throw new Error(`Failed to load projects: ${response.status}`);
    }

    const projects = await response.json();
    const projectLinks = projects.map(createProjectLink);

    projectIndex.replaceChildren(...projectLinks);
}

if (projectIndex) {
    loadProjects().catch((error) => {
        console.error(error);

        showToast(
            'Unable to refresh projects',
            'The server-rendered project list is still available.',
            'error',
        );
    });
}