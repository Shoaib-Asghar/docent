import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const CodeIcon = (props: React.ComponentProps<'svg'>) => (
  <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width: '100px', height: '100px', margin: '0 auto', display: 'block', color: 'var(--ifm-color-primary)'}}>
    <polyline points="16 18 22 12 16 6"></polyline>
    <polyline points="8 6 2 12 8 18"></polyline>
  </svg>
);

const SparkleIcon = (props: React.ComponentProps<'svg'>) => (
  <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width: '100px', height: '100px', margin: '0 auto', display: 'block', color: 'var(--ifm-color-primary)'}}>
    <path d="M12 2l3 7 7 3-7 3-3 7-3-7-7-3 7-3 3-7z"></path>
  </svg>
);

const ServerIcon = (props: React.ComponentProps<'svg'>) => (
  <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width: '100px', height: '100px', margin: '0 auto', display: 'block', color: 'var(--ifm-color-primary)'}}>
    <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
    <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
    <line x1="6" y1="6" x2="6.01" y2="6"></line>
    <line x1="6" y1="18" x2="6.01" y2="18"></line>
  </svg>
);

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'End-to-End Engineering',
    Svg: CodeIcon,
    description: (
      <>
        From scalable web applications to robust microservices, we deliver secure, 
        high-performance software tailored specifically to your business needs.
      </>
    ),
  },
  {
    title: 'AI & Machine Learning',
    Svg: SparkleIcon,
    description: (
      <>
        Unlock the power of artificial intelligence. We build custom RAG pipelines, 
        AI agents, and ML models to automate and scale your complex workflows.
      </>
    ),
  },
  {
    title: 'Secure Infrastructure',
    Svg: ServerIcon,
    description: (
      <>
        Deploy with absolute confidence. Our automation pipelines and DevSecOps practices 
        ensure your infrastructure is secure, resilient, and highly available.
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features} style={{padding: '4rem 0'}}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
