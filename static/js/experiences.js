const experienceList = document.getElementById('experience-list');
const experienceFilterForm = document.getElementById(
    'experience-filter-form',
);
const experienceTitleFilter = document.getElementById(
    'experience-title-filter',
);
const experienceCategoryFilter = document.getElementById(
    'experience-category-filter',
);
const experienceStatusFilter = document.getElementById(
    'experience-status-filter',
);
const experienceFilterClear = document.getElementById(
    'experience-filter-clear',
);
const experienceResultCount = document.getElementById(
    'experience-result-count',
);
const experienceCreateForm = document.getElementById(
    'experience-create-form',
);
const experienceCreateModal = document.getElementById(
    'experience-create-modal',
);
const experienceEditForm = document.getElementById('experience-edit-form');
const experienceEditModal = document.getElementById('experience-edit-modal');
const experienceEditableFields = [
    'title', 'description', 'category', 'thumbnail', 'started_at', 'ended_at',
];
let experienceEditTarget = null;
let experienceEditSaving = false;

const experienceDeleteForm = document.getElementById(
    'experience-delete-form',
);
const experienceDeleteName = document.getElementById(
    'experience-delete-name',
);

let experienceRequestController = null;
const pendingExperienceStars = new Set();
const experiencePlaceholderId = '00000000-0000-0000-0000-000000000000';

function experienceActionUrl(action, id) {
    return experienceList.dataset[action].replace(experiencePlaceholderId, id);
}

function debounce(callback, delay) {
    let timeoutId;

    return (...args) => {
        window.clearTimeout(timeoutId);

        timeoutId = window.setTimeout(() => {
            callback(...args);
        }, delay);
    };
}

function getExperienceFilters() {
    const filters = new URLSearchParams();
    const title = experienceTitleFilter.value.trim();
    const category = experienceCategoryFilter.value;
    const status = experienceStatusFilter.value;

    if (title) {
        filters.set('title', title);
    }

    if (category) {
        filters.set('category', category);
    }

    if (status) {
        filters.set('status', status);
    }

    return filters;
}

function syncExperienceUrl(filters) {
    const query = filters.toString();
    const nextUrl = query
        ? `${window.location.pathname}?${query}`
        : window.location.pathname;

    window.history.replaceState(null, '', nextUrl);
    experienceFilterClear.hidden = !query;
}

function renderExperienceCount(count) {
    const label = count === 1 ? 'experience' : 'experiences';

    experienceResultCount.textContent = `${count} ${label} found`;
}

function createTextElement(tagName, className, text) {
    const element = document.createElement(tagName);

    if (className) {
        element.className = className;
    }

    element.textContent = text;

    return element;
}

function experienceApiErrorMessage(data, status) {
    const messages = data && typeof data === 'object'
        ? Object.values(data).flat().filter(value => typeof value === 'string')
        : [];

    return messages.join(' ') || `Request failed (HTTP ${status}).`;
}

function formatMonthYear(value) {
    const date = new Date(value);

    return new Intl.DateTimeFormat('en', {
        month: 'short',
        year: 'numeric',
    }).format(date);
}

function createTimeElement(value) {
    const time = document.createElement('time');

    time.dateTime = value;
    time.textContent = formatMonthYear(value);

    return time;
}

function updateExperienceStarButton(button, isStarred, starCount) {
    const label = button.querySelector('.experience-star-label');
    const count = button.querySelector('.experience-star-count');

    button.setAttribute('aria-pressed', String(isStarred));
    label.textContent = isStarred ? 'Starred' : 'Star';
    count.textContent = String(starCount);
}

async function toggleExperienceStar(button, experience) {
    if (button.disabled || pendingExperienceStars.has(experience.id)) return;

    pendingExperienceStars.add(experience.id);
    button.disabled = true;

    try {
        const response = await fetch(experienceActionUrl('starUrl', experience.id), {
            method: 'POST',
            headers: {
                'X-CSRFToken': experienceList.dataset.csrfToken,
                Accept: 'application/json',
            },
        });

        const data = await response.json().catch(() => ({}));

        if (response.status !== 200) {
            throw new Error(experienceApiErrorMessage(data, response.status));
        }

        if (
            data.id !== experience.id
            || typeof data.is_starred !== 'boolean'
            || !Number.isInteger(data.star_count)
            || data.star_count < 0
        ) {
            throw new Error('Star update could not be confirmed. Refresh the list before trying again.');
        }

        updateExperienceStarButton(
            button,
            data.is_starred,
            data.star_count,
        );
        syncExperienceStarButtons(experience.id, data);

        // A list request started before the toggle may contain an older star state.
        if (experienceRequestController) {
            await loadExperiences();
        }
    } catch (error) {
        console.error(error);

        showToast(
            'Could not update star',
            error instanceof TypeError ? 'Could not confirm the update. Refresh the list before trying again.' : error.message,
            'error',
        );
    } finally {
        pendingExperienceStars.delete(experience.id);
        button.disabled = false;
        syncExperienceStarButtons(experience.id);
    }
}

function syncExperienceStarButtons(id, data) {
    for (const button of experienceList.querySelectorAll('.experience-star-button')) {
        if (button.dataset.experienceId !== id) continue;

        if (data) {
            updateExperienceStarButton(button, data.is_starred, data.star_count);
        }
        button.disabled = pendingExperienceStars.has(id);
    }
}

function createExperienceStarButton(experience) {
    const button = document.createElement('button');
    const icon = createTextElement('span', '', '★');
    const label = createTextElement(
        'span',
        'experience-star-label',
        '',
    );
    const count = createTextElement(
        'span',
        'experience-star-count',
        '',
    );

    button.type = 'button';
    button.className = 'experience-star-button';
    button.dataset.experienceId = experience.id;
    button.disabled = pendingExperienceStars.has(experience.id);
    icon.setAttribute('aria-hidden', 'true');
    button.append(icon, label, count);
    updateExperienceStarButton(
        button,
        experience.is_starred,
        experience.star_count,
    );
    button.addEventListener('click', () => {
        toggleExperienceStar(button, experience);
    });

    return button;
}

function createExperienceCard(experience) {
    const article = document.createElement('article');
    const header = document.createElement('header');
    const information = document.createElement('div');
    const period = document.createElement('p');
    const points = document.createElement('ul');
    const canStar = experienceList.dataset.canStar === 'true';
    const canChange = experienceList.dataset.canChange === 'true';
    const canDelete = experienceList.dataset.canDelete === 'true';

    article.className = 'experience-item';
    header.className = 'experience-item-header';
    period.className = 'experience-period';
    points.className = 'experience-points';

    information.append(
        createTextElement(
            'p',
            'experience-organization',
            experience.category_label,
        ),
        createTextElement('h2', '', experience.title),
    );

    period.append(
        createTimeElement(experience.started_at),
        document.createTextNode(' – '),
    );

    if (experience.is_ongoing) {
        period.append(document.createTextNode('Present'));
    } else {
        period.append(createTimeElement(experience.ended_at));
    }

    for (const point of experience.description_points) {
        points.append(createTextElement('li', '', point));
    }

    header.append(information, period);
    article.append(header, points);

    if (
        canStar
        || canChange
        || canDelete
    ) {
        const actions = document.createElement('div');

        actions.className = 'experience-actions';

        if (canStar) {
            actions.append(createExperienceStarButton(experience));
        }

        if (canChange) {
            const editLink = createTextElement(
                'a',
                '',
                'Edit experience',
            );

            editLink.href = experienceActionUrl('updateUrl', experience.id);
            editLink.dataset.experienceEditId = experience.id;
            if (experienceEditForm && experienceEditModal) {
                editLink.setAttribute('aria-haspopup', 'dialog');
                editLink.setAttribute('aria-controls', 'experience-edit-modal');
                editLink.addEventListener('click', (event) => {
                    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
                    event.preventDefault();
                    openExperienceEdit(experience, editLink);
                });
            }
            actions.append(editLink);
        }

        if (
            canDelete
            && experienceDeleteForm
            && experienceDeleteName
        ) {
            const deleteButton = createTextElement(
                'button',
                'project-delete-trigger experience-delete-trigger',
                'Delete experience',
            );

            deleteButton.type = 'button';
            deleteButton.setAttribute(
                'popovertarget',
                'experience-delete-modal',
            );
            deleteButton.setAttribute(
                'aria-label',
                `Delete ${experience.title}`,
            );

            deleteButton.addEventListener('click', () => {
                experienceDeleteForm.action = experienceActionUrl('deleteUrl', experience.id);
                experienceDeleteName.textContent = experience.title;
            });

            actions.append(deleteButton);
        }

        article.append(actions);
    }

    if (experience.thumbnail) {
        const thumbnail = document.createElement('img');

        thumbnail.className = 'experience-thumbnail';
        thumbnail.src = experience.thumbnail;
        thumbnail.alt = `Thumbnail for ${experience.title}`;
        thumbnail.loading = 'lazy';

        article.append(thumbnail);
    }

    return article;
}

function renderExperienceLoading() {
    const loading = createTextElement(
        'p',
        'experience-loading',
        'Loading experiences...',
    );

    experienceList.setAttribute('aria-busy', 'true');
    experienceResultCount.textContent = '';
    experienceList.replaceChildren(loading);
}

function renderExperienceEmpty() {
    const filters = getExperienceFilters();
    const message = filters.toString()
        ? 'No experiences match these filters.'
        : 'No experience has been added yet.';
    const emptyState = createTextElement(
        'p',
        'experience-empty',
        message,
    );

    experienceList.setAttribute('aria-busy', 'false');
    renderExperienceCount(0);
    experienceList.replaceChildren(emptyState);
}

function renderExperienceError() {
    const errorState = document.createElement('div');
    const message = createTextElement(
        'p',
        'experience-error-message',
        'Experiences could not be loaded.',
    );
    const retryButton = createTextElement(
        'button',
        'experience-retry',
        'Retry',
    );

    errorState.className = 'experience-error';
    retryButton.type = 'button';
    retryButton.addEventListener('click', loadExperiences);

    errorState.append(message, retryButton);
    experienceList.setAttribute('aria-busy', 'false');
    experienceResultCount.textContent = '';
    experienceList.replaceChildren(errorState);
}

async function loadExperiences() {
    if (experienceRequestController) {
        experienceRequestController.abort();
    }

    const requestController = new AbortController();
    const filters = getExperienceFilters();

    experienceRequestController = requestController;
    renderExperienceLoading();
    syncExperienceUrl(filters);

    const endpoint = new URL(
        experienceList.dataset.experiencesUrl,
        window.location.origin,
    );

    endpoint.search = filters.toString();

    try {
        const response = await fetch(endpoint, {
            headers: {
                Accept: 'application/json',
            },
            signal: requestController.signal,
        });

        if (!response.ok) {
            throw new Error(
                `Failed to load experiences: ${response.status}`,
            );
        }

        const experiences = await response.json();
        // Only the current request may replace the list or its feedback state.
        if (requestController.signal.aborted || experienceRequestController !== requestController) {
            return;
        }

        if (experiences.length === 0) {
            renderExperienceEmpty();
            return;
        }

        const experienceCards = experiences.map(
            createExperienceCard,
        );

        experienceList.setAttribute('aria-busy', 'false');
        renderExperienceCount(experiences.length);
        experienceList.replaceChildren(...experienceCards);
    } catch (error) {
        if (
            error.name === 'AbortError'
            || requestController.signal.aborted
            || experienceRequestController !== requestController
        ) {
            return;
        }

        console.error(error);
        renderExperienceError();

        showToast(
            'Unable to load experiences',
            'Please try again in a moment.',
            'error',
        );
    } finally {
        if (experienceRequestController === requestController) {
            experienceRequestController = null;
        }
    }
}

function openExperienceEdit(experience, trigger) {
    if (experienceEditSaving) return;

    experienceEditForm.reset();
    const initialValues = {};
    for (const name of experienceEditableFields) {
        let value = experience[name] ?? '';
        if ((name === 'started_at' || name === 'ended_at') && value) {
            // The existing HTML form and API interpret datetime-local values in UTC.
            value = new Date(value).toISOString().slice(0, 16);
        }
        experienceEditForm.elements.namedItem(name).value = value;
        initialValues[name] = experienceEditForm.elements.namedItem(name).value;
    }

    experienceEditTarget = { id: experience.id, initialValues, trigger };
    experienceEditForm.action = experienceActionUrl('updateUrl', experience.id);
    experienceEditForm.dataset.apiUrl = experienceActionUrl('detailUrl', experience.id);
    experienceEditModal.showPopover();
    experienceEditForm.elements.namedItem('title').focus();
}

async function submitExperienceEdit(event) {
    event.preventDefault();
    if (experienceEditSaving || !experienceEditTarget) return;

    const target = experienceEditTarget;
    const fields = new FormData(experienceEditForm);
    const payload = {};
    for (const name of experienceEditableFields) {
        const value = fields.get(name);
        if (value !== target.initialValues[name]) {
            payload[name] = (name === 'thumbnail' || name === 'ended_at') && !value
                ? null : value;
        }
    }
    if (Object.keys(payload).length === 0) {
        showToast('No changes', 'Change a field before saving.');
        return;
    }

    const submitButton = experienceEditForm.querySelector('button[type="submit"]');
    experienceEditSaving = true;
    experienceEditForm.setAttribute('aria-busy', 'true');
    for (const name of experienceEditableFields) {
        experienceEditForm.elements.namedItem(name).disabled = true;
    }
    submitButton.disabled = true;
    submitButton.textContent = 'Saving...';

    try {
        const response = await fetch(experienceEditForm.dataset.apiUrl, {
            method: 'PATCH',
            body: JSON.stringify(payload),
            headers: {
                'X-CSRFToken': experienceList.dataset.csrfToken,
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json().catch(() => ({}));
        if (response.status !== 200) {
            throw new Error(experienceApiErrorMessage(data, response.status));
        }
        if (data?.id !== target.id) {
            throw new Error('Update could not be confirmed. Refresh the list before trying again.');
        }

        await loadExperiences();
        experienceEditForm.reset();
        experienceEditModal.hidePopover();
        showToast('Experience updated', 'Experience updated successfully.', 'success');
    } catch (error) {
        console.error(error);
        showToast(
            'Could not update experience',
            error instanceof TypeError ? 'Could not confirm the update. Check the list before trying again.' : error.message,
            'error',
        );
    } finally {
        experienceEditSaving = false;
        experienceEditForm.setAttribute('aria-busy', 'false');
        for (const name of experienceEditableFields) {
            experienceEditForm.elements.namedItem(name).disabled = false;
        }
        submitButton.disabled = false;
        submitButton.textContent = 'Save changes';
    }
}

async function submitExperience(event) {
    event.preventDefault();

    const submitButton = experienceCreateForm.querySelector(
        'button[type="submit"]',
    );
    if (submitButton.disabled) return;

    const csrfToken = experienceCreateForm.querySelector(
        '[name="csrfmiddlewaretoken"]',
    ).value;

    submitButton.disabled = true;

    try {
        const fields = new FormData(experienceCreateForm);
        const payload = Object.fromEntries(
            experienceEditableFields.map(name => [name, fields.get(name)]),
        );
        payload.thumbnail = payload.thumbnail || null;
        payload.ended_at = payload.ended_at || null;

        const response = await fetch(experienceCreateForm.dataset.apiUrl, {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: {
                'X-CSRFToken': csrfToken,
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json().catch(() => ({}));

        if (response.status !== 201) {
            throw new Error(experienceApiErrorMessage(data, response.status));
        }

        experienceCreateForm.reset();
        experienceCreateModal.hidePopover();

        showToast(
            'Experience added',
            'Experience added successfully.',
            'success',
        );

        await loadExperiences();
    } catch (error) {
        console.error(error);

        showToast(
            'Could not add experience',
            error instanceof TypeError ? 'Please try again in a moment.' : error.message,
            'error',
        );
    } finally {
        submitButton.disabled = false;
    }
}

const debouncedLoadExperiences = debounce(loadExperiences, 400);

if (
    experienceList
    && experienceFilterForm
    && experienceTitleFilter
    && experienceCategoryFilter
    && experienceStatusFilter
    && experienceFilterClear
    && experienceResultCount
) {
    experienceFilterForm.addEventListener('submit', (event) => {
        event.preventDefault();
        loadExperiences();
    });

    experienceTitleFilter.addEventListener(
        'input',
        debouncedLoadExperiences,
    );

    experienceCategoryFilter.addEventListener(
        'change',
        loadExperiences,
    );
    experienceStatusFilter.addEventListener(
        'change',
        loadExperiences,
    );

    experienceFilterClear.addEventListener('click', (event) => {
        event.preventDefault();

        experienceTitleFilter.value = '';
        experienceCategoryFilter.value = '';
        experienceStatusFilter.value = '';

        loadExperiences();
    });

    loadExperiences();
}

if (experienceCreateForm && experienceCreateModal) {
    experienceCreateForm.addEventListener(
        'submit',
        submitExperience,
    );
}

if (experienceEditForm && experienceEditModal) {
    experienceEditForm.addEventListener('submit', submitExperienceEdit);
    experienceEditModal.addEventListener('toggle', (event) => {
        if (event.newState !== 'closed' || !experienceEditTarget) return;

        const target = experienceEditTarget;
        experienceEditTarget = null;
        const currentLink = [...experienceList.querySelectorAll('[data-experience-edit-id]')]
            .find(link => link.dataset.experienceEditId === target.id);
        const focusTarget = target.trigger.isConnected ? target.trigger : currentLink;
        (focusTarget ?? experienceTitleFilter).focus({ preventScroll: true });
    });
}
