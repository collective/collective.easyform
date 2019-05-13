#!/bin/sh
domain=collective.easyform
i18ndude rebuild-pot --pot $domain.pot --create $domain ..
i18ndude sync --pot $domain.pot */LC_MESSAGES/$domain.po
i18ndude sync --pot plone.pot */LC_MESSAGES/plone.po