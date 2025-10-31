// Import commands
require('./commands')

// Custom command to select elements by data-cy attribute
Cypress.Commands.add('getBySel', (selector) => {
  return cy.get(`[data-cy="${selector}"]`)
})
