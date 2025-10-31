// Happy Journey Test Data
// Generate unique ID once when module loads - shared across all tests in the same run
const TEST_RUN_ID = Date.now()

const HAPPY_JOURNEY = {
  catalog: {
    name: () => `E2E Catalog ${TEST_RUN_ID}`,
    description: 'E2E Test Catalog for Happy Journey'
  },
  productSpec: {
    name: () => `E2E Product Spec ${TEST_RUN_ID}`,
    description: 'E2E Test Product Specification for Happy Journey',
    version: '0.1',
    brand: 'E2E Test Brand',
    productNumber: '12345'
  },
  offering: {
    name: () => `E2E Offering ${TEST_RUN_ID}`,
    description: 'E2E Test Offering for Happy Journey',
    detailedDescription: 'Additional E2E offering description for Happy Journey',
    version: '0.1'
  },
  pricePlan : {
    name: "pp1"
  },
  priceComponent: {
    name: "pc1",
    price: 5.2,
    type: "one time"
  }
}

module.exports = {
  HAPPY_JOURNEY
}
