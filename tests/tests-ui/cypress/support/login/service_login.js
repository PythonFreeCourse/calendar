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