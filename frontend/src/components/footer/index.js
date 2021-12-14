import styles from './style.module.css'
import { Container, LinkComponent } from '../index'
import cn from 'classnames'

const footerLink = cn(styles.footer__link, styles.footer__brand)

const Footer = () => {
  return <footer className={styles.footer}>
      <Container className={styles.footer__container}>
        <LinkComponent href='#' title='Продуктовый помощник' className={styles.footer__brand} />
        <div className={styles.footer__links}>
          <a className={footerLink} href="https://github.com/dammaer">Автор</a>
          <a className={footerLink} href='https://github.com/dammaer/foodgram-project-react#readme'>Технологии</a>
        </div>
      </Container>
  </footer>
}

export default Footer
