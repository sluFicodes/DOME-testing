// Helper functions for filling forms in the application

/**
 * Create a new catalog
 * @param {Object} params - Catalog parameters
 * @param {string} params.name - Catalog name
 * @param {string} params.description - Catalog description
 */
function createCatalog({ name, description }) {
  cy.visit('/my-offerings')
  cy.getBySel('catalogSection').click()
  cy.getBySel('newCatalog').click()

  // Fill catalog form - Step 1: General info
  cy.getBySel('catalogName').type(name)
  cy.getBySel('catalogDsc').type(description)
  cy.getBySel('catalogNext').click()

  // Step 2: Finish catalog creation
  cy.getBySel('catalogFinish').click()

  // Wait for redirect back to catalog list
  cy.wait(3000)

  // Close feedback modal if it appears
  cy.closeFeedbackModalIfVisible()

  // Verify catalog appears in table
  cy.getBySel('catalogTable').should('be.visible')
  cy.getBySel('catalogTable').contains(name).should('be.visible')
}

/**
 * Update catalog status
 * @param {Object} params - Update parameters
 * @param {string} params.name - Catalog name
 * @param {string} params.status - Status to set
 */
function updateCatalogStatus({ name, status }) {
  cy.getBySel('catalogTable').contains(name).parents('[data-cy="catalogRow"]').find('[data-cy="catalogEdit"]').click()

  if (status === 'launched') {
    cy.getBySel('catalogStatusLaunched').click()
  }

  cy.getBySel('catalogNext').click()
  cy.getBySel('catalogUpdate').click()

  // Close feedback modal if it appears
  cy.closeFeedbackModalIfVisible()
}

/**
 * Create a new product specification
 * @param {Object} params - Product spec parameters
 * @param {string} params.name - Product spec name
 * @param {string} params.version - Version (default: '0.1')
 * @param {string} params.brand - Brand name
 * @param {string} params.productNumber - Product number
 */
function createProductSpec({ name, version = '0.1', brand, productNumber }) {
  cy.visit('/my-offerings')
  cy.getBySel('prdSpecSection').click()
  cy.getBySel('createProdSpec').click()

  // Fill product spec form - Step 1: General info
  cy.getBySel('inputName').type(name)
  cy.getBySel('inputVersion').should('have.value', version)
  cy.getBySel('inputBrand').type(brand)
  cy.getBySel('inputIdNumber').type(productNumber)

  // Navigate through all required steps
  cy.getBySel('btnNext').click() // Go to Bundle step
  cy.getBySel('btnNext').click() // Go to Compliance step
  cy.getBySel('btnNext').click() // Go to Characteristics step
  cy.getBySel('btnNext').click() // Go to Resource step
  cy.getBySel('btnNext').click() // Go to Service step
  cy.getBySel('btnNext').click() // Go to Attachments step
  cy.getBySel('btnFinish').click() // Go to Relationships step

  // Create product spec
  cy.getBySel('btnCreateProduct').should('be.enabled').click()

  // Close feedback modal if it appears
  cy.closeFeedbackModalIfVisible()

  // Verify product spec appears in table
  cy.getBySel('prodSpecTable').should('be.visible')
  cy.getBySel('prodSpecTable').contains(name).should('be.visible')
}

/**
 * Update product spec status
 * @param {Object} params - Update parameters
 * @param {string} params.name - Product spec name
 * @param {string} params.status - Status to set
 */
function updateProductSpecStatus({ name, status }) {
  cy.getBySel('prodSpecTable').contains(name).parents('[data-cy="prodSpecRow"]').find('[data-cy="productSpecEdit"]').click()

  if (status === 'launched') {
    cy.getBySel('productSpecStatusLaunched').click()
  }

  // Navigate through steps to reach update button
  cy.getBySel('btnNext').click() // Bundle step
  cy.getBySel('btnNext').click() // Compliance step
  cy.getBySel('btnNext').click() // Characteristics step
  cy.getBySel('btnNext').click() // Resource step
  cy.getBySel('btnNext').click() // Service step
  cy.getBySel('btnNext').click() // Attachments step
  cy.getBySel('btnFinish').click() // Relationships step

  cy.getBySel('productSpecUpdate').click()

  // Close feedback modal if it appears
  cy.closeFeedbackModalIfVisible()
}

/**
 * Create a new offering
 * @param {Object} params - Offering parameters
 * @param {string} params.name - Offering name
 * @param {string} params.version - Version (default: '0.1')
 * @param {string} params.description - Short description
 * @param {string} params.productSpecName - Product spec to link
 * @param {string} params.catalogName - Catalog to link
 * @param {string} params.detailedDescription - Detailed description
 * @param {string} params.mode - payment mode [free, tailored or paid]
 * @param {Object} params.pricePlan - {name, description}
 * @param {Object} params.priceComponent - {name, description, price, type[one time, recurring, recurring-prepaid, usage], recurringPeriod?, usageInput?}
 * @param {Object} params.procurement - manual, payment-automatic, automatic
 */
function createOffering({
  name,
  version = '0.1',
  description,
  productSpecName,
  catalogName,
  detailedDescription,
  mode,
  pricePlan,
  priceComponent,
  procurement
}) {
  cy.visit('/my-offerings')
  cy.getBySel('offerSection').click()
  cy.getBySel('newOffering').click()

  // Step 1: Basic Information
  cy.getBySel('offerName').type(name)
  cy.getBySel('offerVersion').should('have.value', version)
  cy.getBySel('textArea').type(description)
  cy.getBySel('offerNext').click()

  // Step 2: Select the Product Specification
  cy.getBySel('prodSpecs').contains( productSpecName).click()
  cy.getBySel('offerNext').click()

  // Step 3: Select the Catalog
  cy.getBySel('catalogList').contains(catalogName).click()
  cy.getBySel('offerNext').click()

  // Step 4: Select Category
  // cy.getBySel('categoryList').should('have.length.at.least', 1)
  // cy.getBySel('categoryList').first().click()
  cy.getBySel('offerNext').click()

  // Step 5: Description
  cy.getBySel('textArea').type(detailedDescription)
  cy.getBySel('offerNext').click()

  // Step 6: Pricing (skip for basic offering)
  cy.getBySel('pricePlanType').select(mode)
  if(pricePlan){
      cy.getBySel('newPricePlan').click()
      cy.getBySel('pricePlanName').type(pricePlan.name)
      cy.getBySel('textArea').type(pricePlan.description)
      cy.getBySel('savePricePlan').should('have.attr', 'disabled')
      if(priceComponent){
          cy.getBySel('newPriceComponent').click()
          cy.getBySel('priceComponentName').type(priceComponent.name)
          cy.getBySel('priceComponentDescription').find('[data-cy="textArea"]').type(priceComponent.description)
          cy.getBySel('price').type(String(priceComponent.price))
          cy.getBySel('priceType').select(priceComponent.type)
          if (priceComponent.recurringPeriod){
              cy.getBySel('recurringType').select(priceComponent.recurringPeriod)
          }
          else if (priceComponent.usageInput){
              cy.wait('@usageGET')
              cy.getBySel('usageInput').select(priceComponent.usageInput[0])
              cy.getBySel('usageMetric').select(priceComponent.usageInput[1])
          }
          cy.getBySel('savePriceComponent').click()
      }
      cy.getBySel('savePricePlan').click()
  }
  cy.getBySel('offerNext').click()

  // Step 7: procurement info
  cy.getBySel('procurement').select(procurement)
  cy.getBySel('offerNext').click()

  // Step 8: Finish
  cy.getBySel('offerFinish').click()

  // Close feedback modal if it appears
  cy.closeFeedbackModalIfVisible()

  // Verify offering was created in table
  cy.getBySel('offers').should('be.visible')
  cy.getBySel('offers').contains(name).should('be.visible')
}

/**
 * Update offering status
 * @param {Object} params - Update parameters
 * @param {string} params.name - Offering name
 * @param {string} params.status - Status to set
 */
function updateOffering({ name, status }) {
  cy.getBySel('offers').contains(name).parents('[data-cy="offerRow"]').within(() => {
    cy.get('button[type="button"]').first().click() // Click edit button
  })

  // Wait for edit page to load
  cy.wait(2000)

  // Change status
  if (status === 'launched') {
    cy.getBySel('offerStatusLaunched').click()
    cy.wait(1000)
  }

  // Click update button
  cy.get('button').contains('Update Offer').click()

  // Close feedback modal if it appears
  cy.closeFeedbackModalIfVisible()
}

/**
 * Create checkout billing information
 * @param {Object} params - Billing parameters
 * @param {string} params.title - Title
 * @param {string} params.country - Country
 * @param {string} params.city - City
 * @param {string} params.state - State
 * @param {string} params.zip - Zip code
 * @param {string} params.street - Street address
 * @param {string} params.email - Email address
 * @param {string} params.phoneNumber - Phone number
 */
function createCheckoutBilling({title, country, city, state, zip, street, email, phoneNumber}){
  cy.getBySel('billingTitle').type(title)
  cy.getBySel('billingCountry').select(country)
  cy.getBySel('billingCity').type(city)
  cy.getBySel('billingState').type(state)
  cy.getBySel('billingZip').type(zip)
  cy.getBySel('billingAddress').type(street)
  cy.getBySel('billingEmail').type(email)
  cy.getBySel('billingPhone').parent().find('button').first().click()
  cy.get('ul[aria-labelledby="dropdown-phone-button"]').contains('Spain').scrollIntoView().click()
  cy.getBySel('billingPhone').type(phoneNumber)
  cy.getBySel('addBilling').click()
}

module.exports = {
  createCatalog,
  updateCatalogStatus,
  createProductSpec,
  updateProductSpecStatus,
  createOffering,
  updateOffering,
  createCheckoutBilling
}
