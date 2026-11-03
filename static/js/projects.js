const projectIndex = document.getElementById('project-index');
const projectBrowser = document.getElementById('project-browser');
const projectDetail = document.getElementById('project-detail');
const projectDetailTemplate = document.getElementById('project-detail-template');
const projectFilterClear = document.getElementById('project-filter-clear');
const projectSearchForm = document.getElementById('project-search-form');
const projectSearchInput = document.getElementById('project-search-input');
const projectStarredInput = document.getElementById(
    'project-starred-input',
);
const projectCreateForm = document.getElementById(
    'project-create-form',
);
const projectCreateModal = document.getElementById(
    'project-create-modal',
);

const projectPlaceholderId = '00000000-0000-0000-0000-000000000000';
let selectedProjectId = projectBrowser?.dataset.selectedProjectId || '';
let projectListController;
let projectDetailController;

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

    if (
        projectStarredInput?.checked
        || (!projectStarredInput && projectBrowser.dataset.starredFilter === 'mine')
    ) {
        filters.set('starred', 'mine');
    }

    return filters;
}

function projectPageUrl(id) {
    const url = new URL(
        projectBrowser.dataset.projectPageUrl.replace(projectPlaceholderId, id),
        window.location.origin,
    );
    url.search = getProjectFilters().toString();

    return url;
}

function syncProjectHistory(mode = 'replaceState') {
    const url = selectedProjectId
        ? projectPageUrl(selectedProjectId)
        : new URL(projectSearchForm.action);
    url.search = getProjectFilters().toString();

    window.history[mode]({ projectId: selectedProjectId }, '', url);
    projectFilterClear.hidden = !url.search;
}

function markSelectedProject() {
    for (const link of projectIndex.querySelectorAll('a[data-project-id]')) {
        const selected = link.dataset.projectId === selectedProjectId;
        link.classList.toggle('is-selected', selected);
        if (selected) {
            link.setAttribute('aria-current', 'page');
        } else {
            link.removeAttribute('aria-current');
        }
    }
}

function createProjectLink(project, index) {
    const link = document.createElement('a');
    const number = document.createElement('span');
    const textWrapper = document.createElement('span');
    const title = document.createElement('span');
    const type = document.createElement('span');

    link.className = 'project-index-item';
    link.href = projectPageUrl(project.id);
    link.dataset.projectId = project.id;

    if (selectedProjectId === project.id) {
        link.classList.add('is-selected');
        link.setAttribute('aria-current', 'page');
    }

    number.className = 'project-number';
    number.textContent = String(index + 1).padStart(2, '0');

    title.className = 'project-index-title';
    title.textContent = project.title;

    type.className = 'project-index-type';
    type.textContent = project.project_type;

    textWrapper.append(title, type);
    link.append(number, textWrapper);

    return link;
}

function projectEmptyMessage() {
    const filters = getProjectFilters();
    const title = filters.get('title');
    if (filters.get('starred') === 'mine') {
        return title
            ? `No starred projects match “${title}”.`
            : 'You have not starred any projects yet.';
    }

    return title ? `No projects match “${title}”.` : 'No projects have been added yet.';
}

function showProjectIndexMessage(message) {
    const paragraph = document.createElement('p');
    paragraph.className = 'project-empty';
    paragraph.textContent = message;
    projectIndex.replaceChildren(paragraph);
}

async function loadProjects() {
    projectListController?.abort();
    const controller = new AbortController();
    projectListController = controller;
    projectIndex.setAttribute('aria-busy', 'true');
    const endpoint = new URL(
        projectIndex.dataset.projectsUrl,
        window.location.origin,
    );
    const filters = getProjectFilters();

    endpoint.search = filters.toString();

    const response = await fetch(endpoint, {
        headers: { Accept: 'application/json' },
        signal: controller.signal,
    });

    if (!response.ok) {
        throw new Error(`Failed to load projects: ${response.status}`);
    }

    const projects = await response.json();
    if (controller.signal.aborted) return;

    if (projects.length === 0) {
        showProjectIndexMessage(projectEmptyMessage());
        return;
    }

    const projectLinks = projects.map(createProjectLink);

    projectIndex.replaceChildren(...projectLinks);
}

function handleProjectLoadError(error) {
    if (error.name === 'AbortError') return;
    console.error(error);
    showProjectIndexMessage('Projects could not be loaded. Please try the search again.');

    showToast(
        'Unable to refresh projects',
        'Please try again in a moment.',
        'error',
    );
}

function refreshProjects() {
    syncProjectHistory();
    const request = loadProjects();
    const controller = projectListController;
    return request.catch(error => {
        if (projectListController === controller) handleProjectLoadError(error);
    }).finally(() => {
        if (projectListController === controller) {
            projectIndex.setAttribute('aria-busy', 'false');
        }
    });
}

function showProjectPrompt(title = 'Select a project', message = '') {
    const prompt = document.createElement('div');
    const kicker = document.createElement('p');
    const heading = document.createElement('h2');
    const description = document.createElement('p');
    prompt.className = 'project-prompt';
    kicker.className = 'section-kicker';
    kicker.textContent = 'Project viewer';
    heading.textContent = title;
    description.textContent = message
        || 'Choose a project from the list to see its story, tools, and live result.';
    prompt.append(kicker, heading, description);
    projectDetail.replaceChildren(prompt);
}

function buildProjectDetail(project) {
    const article = projectDetailTemplate.content.firstElementChild.cloneNode(true);
    article.dataset.projectId = project.id;

    // Django renders named routes and role-aware controls in the inert template.
    for (const node of article.querySelectorAll('*')) {
        for (const attribute of ['id', 'href', 'action', 'aria-labelledby', 'popovertarget']) {
            const value = node.getAttribute(attribute);
            if (value?.includes(projectPlaceholderId)) {
                node.setAttribute(attribute, value.replaceAll(projectPlaceholderId, project.id));
            }
        }
    }

    article.querySelector('.project-type').textContent = project.project_type;
    article.querySelector('.project-header h2').textContent = project.title;
    article.querySelector('.project-role').textContent = project.role;
    article.querySelector('.project-summary').textContent = project.description;
    const technologies = project.technologies.split('\n').map(value => value.trim()).filter(Boolean);
    article.querySelector('.project-technologies ul').replaceChildren(
        ...technologies.map(value => {
            const item = document.createElement('li');
            item.textContent = value;
            return item;
        }),
    );

    if (project.thumbnail_path) {
        const preview = document.createElement('img');
        preview.className = 'project-preview';
        const path = project.thumbnail_path.replace(/^\/+/, '')
            .split('/').map(encodeURIComponent).join('/');
        preview.src = `${projectBrowser.dataset.staticUrl}${path}`;
        preview.alt = `Preview of ${project.title}`;
        article.querySelector('.project-header').after(preview);
    }

    const liveLink = article.querySelector('.project-live-link');
    liveLink.href = project.live_url;
    if (project.source_url) {
        const source = document.createElement('a');
        source.className = 'project-source-link';
        source.href = project.source_url;
        source.target = '_blank';
        source.rel = 'noopener noreferrer';
        source.textContent = 'Source';
        liveLink.after(source);
    }

    const starButton = article.querySelector('.project-star-button');
    if (starButton) {
        starButton.setAttribute('aria-pressed', String(project.is_starred));
        starButton.querySelector('.project-star-label').textContent = project.is_starred ? 'Starred' : 'Star';
        starButton.querySelector('.project-star-count').textContent = String(project.star_count);
    }
    const deleteButton = article.querySelector('.project-delete-trigger');
    if (deleteButton) {
        deleteButton.setAttribute('aria-label', `Delete ${project.title}`);
        article.querySelector('.project-delete-modal-content strong').textContent = project.title;
    }

    return article;
}

async function selectProject(id, { pushHistory = false } = {}) {
    projectDetailController?.abort();
    const controller = new AbortController();
    projectDetailController = controller;
    const previousId = selectedProjectId;
    selectedProjectId = id || '';
    markSelectedProject();
    if (pushHistory) {
        syncProjectHistory(previousId === selectedProjectId ? 'replaceState' : 'pushState');
    }

    if (!id) {
        showProjectPrompt();
        projectDetail.setAttribute('aria-busy', 'false');
        return;
    }

    projectDetail.setAttribute('aria-busy', 'true');
    try {
        const endpoint = projectBrowser.dataset.projectDetailUrl.replace(projectPlaceholderId, id);
        const response = await fetch(endpoint, {
            headers: { Accept: 'application/json' },
            signal: controller.signal,
        });
        if (!response.ok) throw new Error(`Failed to load project: ${response.status}`);
        const project = await response.json();
        if (!controller.signal.aborted) {
            projectDetail.replaceChildren(buildProjectDetail(project));
        }
    } catch (error) {
        if (error.name === 'AbortError' || controller.signal.aborted) return;
        console.error(error);
        showProjectPrompt('Project could not be loaded', 'Select the project again to retry.');
        showToast('Unable to load project', 'Please try again in a moment.', 'error');
    } finally {
        if (projectDetailController === controller) {
            projectDetail.setAttribute('aria-busy', 'false');
        }
    }
}

function getFirstFormError(errors) {
    const errorGroups = Object.values(errors);
    const firstError = errorGroups.flat()[0];

    return firstError?.message ?? 'Please check the project form.';
}

async function submitProject(event) {
    event.preventDefault();

    const submitButton = projectCreateForm.querySelector(
        'button[type="submit"]',
    );
    const csrfToken = projectCreateForm.querySelector(
        '[name="csrfmiddlewaretoken"]',
    ).value;

    submitButton.disabled = true;

    try {
        const response = await fetch(projectCreateForm.action, {
            method: 'POST',
            body: new FormData(projectCreateForm),
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
        });
        const data = await response.json();

        if (!response.ok) {
            showToast(
                'Could not add project',
                getFirstFormError(data.errors),
                'error',
            );
            return;
        }

        projectCreateForm.reset();
        projectCreateModal.hidePopover();

        showToast(
            'Project added',
            data.message,
            'success',
        );

        if (projectIndex) {
            refreshProjects();
        } else {
            window.location.reload();
        }
    } catch (error) {
        console.error(error);

        showToast(
            'Could not add project',
            'Please try again in a moment.',
            'error',
        );
    } finally {
        submitButton.disabled = false;
    }
}

const debouncedRefreshProjects = debounce(refreshProjects, 400);

if (projectBrowser && projectIndex && projectDetail && projectSearchForm && projectSearchInput) {
    projectIndex.addEventListener('click', event => {
        const link = event.target.closest('a[data-project-id]');
        if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        selectProject(link.dataset.projectId, { pushHistory: true });
    });

    projectFilterClear.addEventListener('click', event => {
        event.preventDefault();
        projectSearchInput.value = '';
        if (projectStarredInput) projectStarredInput.checked = false;
        projectBrowser.dataset.starredFilter = '';
        selectProject('', { pushHistory: true });
        refreshProjects();
    });

    window.addEventListener('popstate', event => {
        const filters = new URLSearchParams(window.location.search);
        projectSearchInput.value = filters.get('title') || '';
        if (projectStarredInput) projectStarredInput.checked = filters.get('starred') === 'mine';
        projectBrowser.dataset.starredFilter = filters.get('starred') || '';
        selectProject(event.state?.projectId || '');
        refreshProjects();
    });
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
    if (selectedProjectId) selectProject(selectedProjectId);
}

if (projectCreateForm && projectCreateModal) {
    projectCreateForm.addEventListener(
        'submit',
        submitProject,
    );
}
