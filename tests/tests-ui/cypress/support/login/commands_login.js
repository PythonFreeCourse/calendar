Cypress.Commands.add("loginUI", (user, password) => { 
    if(user == null){
		user = Cypress.env('user');
		password = Cypress.env('password');
	}
	login(user,password);
	cy.get('.header-menu-buttons').should('contain', user)
})

Cypress.Commands.add("loginError", (user,password) => {
	login(user,password);
	cy.get('.callout').should('contain', 'Incorrect username or password');
})


function login(user,password) {
	cy.visit("/login")
	cy.get('input[name=\'username\']')
			.type(user)
	cy.get('input[name=\'password\']')
			.type(password)
	cy.get('.btn').click()
}

Cypress.Commands.add("logoutUI", () => {
	cy.get(".icon-account_circle").click();
	cy.get(".icon-sign-out").click();
	cy.get('.btn').should('be.visible');

})