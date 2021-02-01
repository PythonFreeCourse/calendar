import {check_level} from '../../support/index'
import {screen_sizes_dict} from '../../support/enums/sizes'
import { pages } from '../../support/enums/enums';


describe('HomePage tests', () => {
    for (const [key, sizes] of Object.entries(screen_sizes_dict)) {
        sizes.forEach(size => {
            it(`Visit Calendar home page on ${key} size: ${size}`, { testLevel: 1 }, () => {
                // Checks home page page on different screen sizes

                if (check_level(Cypress.config('testLevel'))) return

                if (Cypress._.isArray(size)) {
                    cy.viewport(size[0], size[1])
                } else {
                    cy.viewport(size)
                }
                cy.visit(pages.HOME)
                cy.contains('Calendar') 
            });
    
            //cy.url().should('include', '/signIn')

            //cy.get('.signIn_input[name=email]')
            //.type('fake@email.com')
            //.should('have.value', 'fake@email.com')
        })
    }
})