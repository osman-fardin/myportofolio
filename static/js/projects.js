const projectIndex = document.getElementById('project-index');
const projectSearchForm = document.getElementById('project-search-form');
const projectSearchInput = document.getElementById('project-search-input');
const projectStarredInput = document.getElementById(
    'project-starred-input',
);


function debounce(callback, delay) {
    let timeoutId;

    return (...args) => {
        window.clearTimeout(timeoutId);

        timeoutId = window.setTimeout(() => {
            callback(...args);
        }, delay);
    };
}

function getProjectFilters() {
    const filters = new URLSearchParams();
    const titleQuery = projectSearchInput.value.trim();

    if (titleQuery) {
        filters.set('title', titleQuery);
    }

    if (projectStarredInput?.checked) {
        filters.set('starred', 'mine');
    }

    return filters;
}

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
    const filters = getProjectFilters();

    endpoint.search = filters.toString();

    const response = await fetch(endpoint);

    if (!response.ok) {
        throw new Error(`Failed to load projects: ${response.status}`);
    }

    const projects = await response.json();

    if (projects.length === 0) {
        const emptyState = document.createElement('p');

        emptyState.className = 'project-empty';
        emptyState.textContent = 'No projects match these filters.';

        projectIndex.replaceChildren(emptyState);
        return;
    }

    const projectLinks = projects.map(createProjectLink);

    projectIndex.replaceChildren(...projectLinks);
}

function handleProjectLoadError(error) {
    console.error(error);

    showToast(
        'Unable to refresh projects',
        'Please try again in a moment.',
        'error',
    );
}

function refreshProjects() {
    loadProjects().catch(handleProjectLoadError);
}

const debouncedRefreshProjects = debounce(refreshProjects, 400);

if (projectIndex && projectSearchForm && projectSearchInput) {
    projectSearchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        refreshProjects();
    });

    projectSearchInput.addEventListener(
        'input',
        debouncedRefreshProjects,
    );

    if (projectStarredInput) {
        projectStarredInput.addEventListener(
            'change',
            refreshProjects,
        );
    }

    refreshProjects();
}