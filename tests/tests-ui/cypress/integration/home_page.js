import {check_level} from '../support/index'
import {screen_sizes_dict} from '../enums/sizes'


describe('HomePage tests', () => {
    for (const [key, sizes] of Object.entries(screen_sizes_dict)) {
        sizes.forEach(size => {
            it(`Visit Calendar home page on ${key} size: ${size}`, { testLevel: 1 }, () => {
                if (check_level(Cypress.config('testLevel'))) return
                if (Cypress._.isArray(size)) {
                    cy.viewport(size[0], size[1])
                } else {
                    cy.viewport(size)
                }
                cy.visit('/')
                cy.contains('Calendar') 
        });
    
            //cy.url().should('include', '/signIn')

            //cy.get('.signIn_input[name=email]')
            //.type('fake@email.com')
            //.should('have.value', 'fake@email.com')
        })
    }

    it('Files upload tests', { 'testLevel': 6 }, () => {
        if (check_level(Cypress.config('testLevel'))) return

        expect(1+2).to.equal(3) 
    })
})