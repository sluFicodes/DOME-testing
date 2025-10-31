// Credenciales del usuario admin creado en el testing.sh
const ADMIN_USER = {
  email: 'admin@test.com',
  password: '1234',
  username: 'admin'
}

// Roles asignados al usuario admin en el testing.sh
const ROLES = {
  SELLER: 'seller',
  CUSTOMER: 'customer',
  ADMIN: 'admin',
  ORG_ADMIN: 'orgAdmin'
}

const ORGS = {
  SELLER: 'SELLER ORG',
  BUYER: 'BUYER ORG'
}

module.exports = {
  ADMIN_USER,
  ROLES
}
