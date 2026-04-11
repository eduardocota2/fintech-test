from app.db.utils.enums import ApplicationStatus


CountryTransitions = dict[ApplicationStatus, tuple[ApplicationStatus, ...]]
