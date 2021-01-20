import {check_level} from '../../support/index'


describe('Profile page tests', () => {
    beforeEach(() => {
        //cy.logIn(true);
    })

    after(() => {
        //cy.logOut();
    })

    it(`Visit Calendar profile page on ${key} size: ${size}`, { testLevel: 1 }, () => {
        // Checks home page page on different screen sizes

        if (check_level(Cypress.config('testLevel'))) return

        if (Cypress._.isArray(size)) {
            cy.viewport(size[0], size[1])
        } else {
            cy.viewport(size)
        }
        cy.visit('/profile')
        cy.contains('Settings') 
    });  
})