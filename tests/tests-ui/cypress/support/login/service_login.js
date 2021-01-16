Cypress.Commands.add("login_service", (userName = Cypress.env('user'), passWord = Cypress.env('password')) => {
	cy.request({
		method: 'POST',
		url: `/login`,
		qs: {
			username: userName,
			password: passWord,
		}
	})
})

Cypress.Commands.add("logout_service", () => {
	cy.request({
		method: 'POST',
		url: `/logout`,
	})
})