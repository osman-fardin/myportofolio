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

const experienceDeleteForm = document.getElementById(
    'experience-delete-form',
);
const experienceDeleteName = document.getElementById(
    'experience-delete-name',
);

let experienceRequestController = null;

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

function getFirstFormError(errors = {}) {
    const errorGroups = Object.values(errors);
    const firstError = errorGroups.flat()[0];

    return firstError?.message ?? 'Please check the experience form.';
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
    button.disabled = true;

    try {
        const response = await fetch(experience.star_url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': experienceList.dataset.csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
                Accept: 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(
                `Failed to update experience star: ${response.status}`,
            );
        }

        const data = await response.json();

        updateExperienceStarButton(
            button,
            data.is_starred,
            data.star_count,
        );
    } catch (error) {
        console.error(error);

        showToast(
            'Could not update star',
            'Please try again in a moment.',
            'error',
        );
    } finally {
        button.disabled = false;
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
        experience.can_star
        || experience.can_change
        || experience.can_delete
    ) {
        const actions = document.createElement('div');

        actions.className = 'experience-actions';

        if (experience.can_star) {
            actions.append(createExperienceStarButton(experience));
        }

        if (experience.can_change) {
            const editLink = createTextElement(
                'a',
                '',
                'Edit experience',
            );

            editLink.href = experience.update_url;
            actions.append(editLink);
        }

        if (
            experience.can_delete
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
                experienceDeleteForm.action = experience.delete_url;
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
        if (error.name === 'AbortError') {
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

async function submitExperience(event) {
    event.preventDefault();

    const submitButton = experienceCreateForm.querySelector(
        'button[type="submit"]',
    );
    const csrfToken = experienceCreateForm.querySelector(
        '[name="csrfmiddlewaretoken"]',
    ).value;

    submitButton.disabled = true;

    try {
        const response = await fetch(experienceCreateForm.action, {
            method: 'POST',
            body: new FormData(experienceCreateForm),
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
                Accept: 'application/json',
            },
        });
        const data = await response.json();

        if (!response.ok) {
            showToast(
                'Could not add experience',
                data.message ?? getFirstFormError(data.errors),
                'error',
            );
            return;
        }

        experienceCreateForm.reset();
        experienceCreateModal.hidePopover();

        showToast(
            'Experience added',
            data.message,
            'success',
        );

        await loadExperiences();
    } catch (error) {
        console.error(error);

        showToast(
            'Could not add experience',
            'Please try again in a moment.',
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
