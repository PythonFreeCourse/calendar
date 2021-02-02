/// <reference types="cypress" />


Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false
});

context('Navigation Test', () => {
    beforeEach(() => {
        cy.visit('http://127.0.0.1:8000/')
    });

    describe('Navigation Test', () => {

        it('Home page has activated', () => {
            cy.get('body').type('{alt}{c}{h}');
            cy.contains('Hello');
        });

        it('Profile page has activated', () => {
            cy.get('body').type('{alt}{c}{p}');
            cy.contains('Explore');
        });

        it('Agenda page has activated', () => {
            cy.get('body').type('{alt}{c}{a}');
            cy.contains('Next Week');
        });

        it('Invitations page has activated', () => {
            cy.get('body').type('{alt}{c}{i}');
            cy.contains('You don\'t have any invitations.');
        });

        it('Search page has activated', () => {
            cy.get('body').type('{alt}{c}{s}');
            cy.contains('Hello');
        });

        it('Keyboard shortcuts page has activated', () => {
            cy.get('body').type('{ctrl}.');
            cy.contains('General');
        });
    });
});
