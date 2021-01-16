import {check_level} from '../support/index'
const sizes = [[1024, 768]]

describe('HomePage tests', () => {
    sizes.forEach((size) => {
        it(`Visits Store Me App home page on ${size}`, { testLevel: 1 }, () => {
            if (Cypress._.isArray(size)) {
                cy.viewport(size[0], size[1])
            } else {
                cy.viewport(size)
            }
            cy.visit('/')
            //cy.contains('Sign In').click()
            //cy.url().should('include', '/signIn')

            //cy.get('.signIn_input[name=email]')
            //.type('fake@email.com')
            //.should('have.value', 'fake@email.com')
        })
    })

    it('Files upload tests', { 'testLevel': 6 }, () => {
        if (check_level(Cypress.config('testLevel'))) return

        expect(1+2).to.equal(3) 
    })
})