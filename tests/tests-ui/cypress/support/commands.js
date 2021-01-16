export function randomStr(name) {
	if (name == null) {
		name = "";
	}
	return name + Math.random().toString(36).slice(-5)
}

Cypress.Commands.add('refresh', (timeToWait = 0) => {
	cy.reload(true);
	cy.wait(timeToWait);
})

Cypress.Commands.add('commonBeforeEach', () => {
	cy.login_service();
})

Cypress.Commands.add('commonAfter', () => {
    cy.log('After');
    cy.logout_service();
})