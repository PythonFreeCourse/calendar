import {check_level} from '../../support/index'
import {update_dropdown, form_name} from '../../support/enums/enums_profilePage'
import {pages} from '../../support/enums/enums'

describe('User card actions', () => {
    beforeEach(() => {
        //cy.logIn(true);
    })

    after(() => {
        //cy.logOut();
    })

    it(`Update name`, { testLevel: 1 }, () => {
        if (check_level(Cypress.config('testLevel'))) return

        cy.visit(pages.PROFILE)
        cy.clickEditButton()
        cy.clickEditRow(update_dropdown.NAME)
        cy.randomStr("newName").then((new_name => {
            cy.updateTextModal(form_name.NAME_FORM, new_name)
            cy.get('.card-title[id="user_fullName"]').should('have.text', new_name)
        })) 
    });

    it(`Update about me`, { testLevel: 1 }, () => {
        if (check_level(Cypress.config('testLevel'))) return

        cy.visit(pages.PROFILE)
        cy.clickEditButton()
        cy.clickEditRow(update_dropdown.ABOUT_ME)
        cy.randomStr("newDescription").then((new_description => {
            cy.updateTextModal(form_name.ABOUT_ME_FORM, new_description)
            cy.get('[id="description"]').contains(new_description).should('exist')
        })) 
    });
})