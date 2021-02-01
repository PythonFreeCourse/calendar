import {button} from '../enums/enums'


Cypress.Commands.add("clickEditButton", () => {
    cy.get(`.dropdown [id='dropdownMenuButton']`).click()
})

Cypress.Commands.add("clickEditRow", (row_name) => {
    cy.get(`.btn[data-bs-target='${row_name}']`).click()
})

Cypress.Commands.add("updateTextModal", (form_name, text) => {
    cy.get(`form[action='${form_name}'] input`).clear().type(text)
    cy.click_button(form_name, button.SUBMIT)
})