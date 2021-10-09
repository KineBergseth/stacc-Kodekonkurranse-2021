import dash_bootstrap_components as dbc


def Navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Marketplace", href="/marketplace")),
            dbc.NavItem(dbc.NavLink("Collections", href="/collections")),
            dbc.NavItem(dbc.NavLink("Upload NFT", href="/upload")),
            dbc.NavItem(dbc.NavLink("Profile", href="/profile")),

        ],
        brand="Home",
        brand_href="/home",
        sticky="top",
        color="dark",
        dark=True,
        expand="md",
    )
    return navbar
