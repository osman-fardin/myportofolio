const experienceList = document.getElementById('experience-list');

const experienceDeleteForm = document.getElementById(
    'experience-delete-form',
);
const experienceDeleteName = document.getElementById(
    'experience-delete-name',
);

function createTextElement(tagName, className, text) {
    const element = document.createElement(tagName);

    if (className) {
        element.className = className;
    }

    element.textContent = text;

    return element;
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

    if (experience.can_change || experience.can_delete) {
        const actions = document.createElement('div');

        actions.className = 'experience-actions';

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
    experienceList.replaceChildren(loading);
}

function renderExperienceEmpty() {
    const filters = new URLSearchParams(window.location.search);
    const message = filters.toString()
        ? 'No experiences match these filters.'
        : 'No experience has been added yet.';
    const emptyState = createTextElement(
        'p',
        'experience-empty',
        message,
    );

    experienceList.setAttribute('aria-busy', 'false');
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
    experienceList.replaceChildren(errorState);
}

async function loadExperiences() {
    renderExperienceLoading();

    const endpoint = new URL(
        experienceList.dataset.experiencesUrl,
        window.location.origin,
    );

    endpoint.search = window.location.search;

    try {
        const response = await fetch(endpoint, {
            headers: {
                Accept: 'application/json',
            },
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
        experienceList.replaceChildren(...experienceCards);
    } catch (error) {
        console.error(error);
        renderExperienceError();

        showToast(
            'Unable to load experiences',
            'Please try again in a moment.',
            'error',
        );
    }
}

if (experienceList) {
    loadExperiences();
}
